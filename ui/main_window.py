# Joao Victor Fagundes
# Salomao Rodrigues Jacinto
# INE5421 - Trabalho Prático I Junho 2018

import re
from model.grammar import Grammar
from model.regex import Regex
from model.automata import Automata
from ui.main_window_ui import Ui_MainWindow
from PyQt5 import QtCore
from PyQt5.QtWidgets import (
    QMainWindow, QMessageBox, QInputDialog, QFileDialog, QTableWidgetItem)

SYMBOL_INPUT='(([a-z0-9],)?)*[a-z0-9]'
STATE_INPUT='(([q][0-9]*,)?)*q[0-9]*|qErro'
INITIAL_GRAMMAR='[A-Z][\']*->[a-z0-9&]([A-Z][\']*)?(\|[a-z0-9&]([A-Z][\']*)?)*'
GRAMMAR_INPUT='[A-Z][\']*->[a-z0-9]([A-Z][\']*)?(\|[a-z0-9]([A-Z][\']*)?)*'

class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.message = QMessageBox()
        self.message.setIcon(QMessageBox.Information)

        self._regex = Regex()
        self._automata = Automata()
        self._grammar = Grammar()
        self._automata_list = list()
        self._item_data = ''
        self._table_data = ''

        #Regex
        self.importRegexButton.clicked.connect(self.import_regex)
        self.exportRegexButton.clicked.connect(self.export_regex)
        self.convertRegexButton.clicked.connect(self.convert_regex)

        #Automata
        self.importAutomataButton.clicked.connect(self.import_automata)
        self.exportAutomataButton.clicked.connect(self.export_automata)
        self.convertAutomataButton.clicked.connect(self.convert_automata)
        self.addStateButton.clicked.connect(self.add_state)
        self.removeStateButton.clicked.connect(self.remove_state)
        self.addSymbolButton.clicked.connect(self.add_symbol)
        self.removeSymbolButton.clicked.connect(self.remove_symbol)
        self.setFinalStatesButton.clicked.connect(self.set_final_states)
        self.enumerateButton.clicked.connect(self.enumerate_strings)
        self.checkStringButton.clicked.connect(self.check_string)
        self.transitionTable.itemClicked.connect(self.table_item_clicked)
        self.transitionTable.itemDoubleClicked.connect(self.table_item_double_clicked)
        self.transitionTable.cellChanged.connect(self.update_automata)

        #Grammar
        self.importGrammarButton.clicked.connect(self.import_grammar)
        self.exportGrammarButton.clicked.connect(self.export_grammar)
        self.convertGrammarButton.clicked.connect(self.convert_grammar)
        self.addProdButton.clicked.connect(self.add_production)
        self.removeProdButton.clicked.connect(self.remove_production)
        self.productionList.itemClicked.connect(self.grammar_item_clicked)
        self.productionList.itemDoubleClicked.connect(self.grammar_item_double_clicked)
        self.productionList.itemChanged.connect(self.update_grammar)

        #Automata List
        self.automataList.itemDoubleClicked.connect(self.automata_list_double_clicked)

        #Operations
        self.actionIntersection.triggered.connect(self.intersection_action)
        self.actionDifference.triggered.connect(self.difference_action)
        self.actionReverse.triggered.connect(self.reverse_action)
        self.actionDeterminize.triggered.connect(self.determinize_action)
        self.actionMinimize.triggered.connect(self.minimize_action)
        self.actionUnion.triggered.connect(self.union_action)
        self.actionConcatenation.triggered.connect(self.concatenation_action)
        self.actionClosure.triggered.connect(self.closure_action)
        self.actionComplement.triggered.connect(self.complement)

    def add_automata_to_list(self):
        if self.transitionTable.rowCount() != 0 and self.transitionTable.columnCount() != 0:
            text, ok = QInputDialog.getText(self, 'Replace Automata', 'You are going to '+
                            'replace the current automata, give it a name or cancel to '+
                            'not add it to the list: ')
            if ok:
                new_automata = self._automata.copy()
                self._automata_list.append(new_automata)
                self.automataList.addItem(text)

    def automata_list_double_clicked(self, item):
        self.add_automata_to_list()
        index = self.automataList.row(item)
        self._automata = self._automata_list[index]
        self.update_transition_table()

    def import_regex(self):
        path, _ = QFileDialog.getOpenFileName(self)
        self._regex = Regex()
        if path:
            try:
                self._regex.load(path)
                self.regexInput.setText(self._regex.string)
            except ValueError as error:
                QMessageBox.critical(self, 'Error', error.args[0])

    def export_regex(self):
        regex_string = self.regexInput.text()
        self._regex = Regex(regex_string)
        path, _ = QFileDialog.getSaveFileName(self)
        if path:
            self._regex.save(path)

    def convert_regex(self):
        regex_string = self.regexInput.text()
        self._regex = Regex(regex_string)
        self.add_automata_to_list()
        self._automata = self._regex.convert_to_automata()
        self.update_transition_table()

    def validate_finite_automata(self, automata):
        if re.fullmatch(STATE_INPUT, automata.initial_state) is None:
            return False
        symbols = ','.join(sorted(automata.symbols))
        if re.fullmatch(SYMBOL_INPUT, symbols) is None:
            return False
        states = ','.join(sorted(automata.states))
        if re.fullmatch(STATE_INPUT, states) is None:
            return False
        final_states = ','.join(sorted(automata.final_states))
        if final_states != '':
            if re.fullmatch(STATE_INPUT, final_states) is None:
                return False

        transitions = [','.join(sorted(v)) for k, v in automata.transitions.items()]
        for transition in transitions:
            if transition != '':
                if re.fullmatch(STATE_INPUT, transition) is None:
                    return False

        return True

    def import_automata(self):
        path, _ = QFileDialog.getOpenFileName(self)
        if path:
            try:
                automata = Automata()
                automata.load(path)
                if self.validate_finite_automata(automata):
                    self.add_automata_to_list()
                    self._automata = automata
                    self.update_transition_table()
                else:
                    QMessageBox.critical(self, 'Error', 'Not a valid automata')

            except ValueError as error:
                QMessageBox.critical(self, 'Error', error.args[0])

    def export_automata(self):
        path, _ = QFileDialog.getSaveFileName(self)
        if path:
            self._automata.save(path)

    def convert_automata(self):
        if self.transitionTable.rowCount() != 0 and self.transitionTable.columnCount() != 0:
            self._grammar = self._automata.convert_to_grammar()
            self.update_grammar_list()

    def add_state(self):
        text, ok = QInputDialog.getText(
            self, 'Add State', 'You can input a single state qN or a list of '+
                               'states. e.g(q0, q1, ...)')
        if ok:
            text = text.strip().replace(' ', '')
            while re.fullmatch(STATE_INPUT, text) is None:
                text, ok = QInputDialog.getText(self, 'Add State',
                    'The states have to be a \'q\' followed by a number')
                if ok:
                    text = text.strip().replace(' ', '')

            for state in text.split(','):
                self._automata.add_state(state)
                for s in self._automata.symbols:
                    self._automata.transitions[state, s] = set()
                self.update_transition_table()

    def remove_state(self):
        text, ok = QInputDialog.getText(
            self, 'Remove State', 'You can input a single state qN or a list of '+
                               'states. e.g(q0, q1, ...)')
        if ok:
            text = text.strip().replace(' ', '')
            while re.fullmatch(STATE_INPUT, text) is None:
                text, ok = QInputDialog.getText(self, 'Remove State',
                    'The states have to be a \'q\' followed by a number')
                if ok:
                    text = text.strip().replace(' ', '')

            for state in text.split(','):
                self._automata.remove_state(state)
                self.update_transition_table()

    def add_symbol(self):
        text, ok = QInputDialog.getText(
            self, 'Add Symbol', 'You can input a single symbol or a list of '+
                                'symbols. e.g(a, b, c, ...)')

        if ok:
            text = text.strip().replace(' ', '')
            while re.fullmatch(SYMBOL_INPUT, text) is None:
                text, ok = QInputDialog.getText(self, 'Add Symbol',
                    'Only lower case letters and numbers are accepted as symbols!')
                if ok:
                    text = text.strip().replace(' ', '')

            for symbol in text.split(','):
                self._automata.add_symbol(symbol)
                for state in self._automata.states:
                    self._automata.transitions[state, symbol] = set()
                self.update_transition_table()

    def remove_symbol(self):
        text, ok = QInputDialog.getText(
            self, ' Remove Symbol', 'You can input a single symbol or a list of '+
                                'symbols. e.g(a, b, c, ...)')

        if ok:
            text = text.strip().replace(' ', '')
            while re.fullmatch(SYMBOL_INPUT, text) is None:
                text, ok = QInputDialog.getText(self, 'Remove Symbol',
                    'Only lower case letters and numbers are accepted as symbols!')
                if ok:
                    text = text.strip().replace(' ', '')

            for symbol in text.split(','):
                self._automata.remove_symbol(symbol)
                self.update_transition_table()

    def set_final_states(self):
        text, ok = QInputDialog.getText(
            self, 'Set Final States', 'You can input a single state qN or a list of '+
                               'states. e.g(q0, q1, ...)')

        if ok:
            text = text.strip().replace(' ', '')
            while re.fullmatch(STATE_INPUT, text) is None:
                text, ok = QInputDialog.getText(self, 'Set Final States',
                    'The states have to be a \'q\' followed by a number')
                if ok:
                    text = text.strip().replace(' ', '')

            for state in text.split(','):
                self._automata.add_final_state(state)
                self.update_transition_table()

    def determinize_action(self):
        self.add_automata_to_list()
        self._automata.determinize()
        self._automata.rename_states()
        self.update_transition_table()

    def minimize_action(self):
        self.add_automata_to_list()
        self._automata.minimize()
        self._automata.rename_states()
        self.update_transition_table()

    def union_action(self):
        try:
            item_text = self.automataList.selectedItems()[0].text()
            message = ('Union will be made with the current automata and the selected '+
                    'automata from the list: ' + item_text + '.')
            ok = QMessageBox.question(self, 'Select Automata', message, 
                                    QMessageBox.Yes, QMessageBox.No)
            if ok == QMessageBox.Yes:
                self.add_automata_to_list()
                other_automata = self._automata_list[self.automataList.currentRow()].copy()
                self._automata.union(other_automata)
                self.update_transition_table()
        
        except IndexError:
            self.message.setText('To use union operation you need a automata in '+
                                 'the table and other selected from the automata list!')
            self.message.show()

    def concatenation_action(self):
        try:
            item_text = self.automataList.selectedItems()[0].text()
            message = ('Concatenation will be made with the current automata and the selected '+
                    'automata from the list: ' + item_text + '.')
            ok = QMessageBox.question(self, 'Select Automata', message, 
                                    QMessageBox.Yes, QMessageBox.No)
            if ok == QMessageBox.Yes:
                self.add_automata_to_list()
                other_automata = self._automata_list[self.automataList.currentRow()].copy()
                self._automata.concatenation(other_automata)
                self.update_transition_table()
        
        except IndexError:
            self.message.setText('To use union operation you need a automata in '+
                                 'the table and other selected from the automata list!')
            self.message.show()

    def closure_action(self):
        self.add_automata_to_list()
        self._automata.closure()
        self.update_transition_table()

    def complement(self):
        self.add_automata_to_list()
        self._automata.complement()
        self.update_transition_table()

    def intersection_action(self):
        try:
            item_text = self.automataList.selectedItems()[0].text()
            message = ('Intersection will be made with the current automata and the selected '+
                    'automata from the list: ' + item_text + '.')
            ok = QMessageBox.question(self, 'Select Automata', message, 
                                    QMessageBox.Yes, QMessageBox.No)
            if ok == QMessageBox.Yes:
                self.add_automata_to_list()
                other_automata = self._automata_list[self.automataList.currentRow()].copy()
                (o, s, u) = self._automata.intersection(other_automata)
                self.automataList.addItem(item_text+'Complement')
                self.automataList.addItem('oldAutomataComplement')
                self.automataList.addItem('middleComplementUnion')
                self._automata_list.append(o)
                self._automata_list.append(s)
                self._automata_list.append(u)
                self.update_transition_table()
        
        except IndexError:
            self.message.setText('To use intersection operation you need a automata in '+
                                 'the table and other selected from the automata list!')
            self.message.show()

    def difference_action(self):
        try:
            item_text = self.automataList.selectedItems()[0].text()
            message = ('Difference will be made with the current automata - selected '+
                    'automata from the list: ' + item_text + '.')
            ok = QMessageBox.question(self, 'Select Automata', message, 
                                    QMessageBox.Yes, QMessageBox.No)
            if ok == QMessageBox.Yes:
                self.add_automata_to_list()
                other_automata = self._automata_list[self.automataList.currentRow()].copy()
                o = self._automata.difference(other_automata)
                self.automataList.addItem(item_text+'Complement')
                self._automata_list.append(o)
                self.update_transition_table()
        
        except IndexError:
            self.message.setText('To use intersection operation you need a automata in '+
                                 'the table and other selected from the automata list!')
            self.message.show()

    def reverse_action(self):
        self.add_automata_to_list()
        self._automata.reverse()
        self.update_transition_table()

    def enumerate_strings(self):
        n, ok = QInputDialog.getInt(
            self, 'Enumerate', 'Which size of sentence')
        if ok:
            try:
                accepted = self._automata.enumerate_strings(n)
                if accepted == set():
                    accepted = 'There aren\'t sentences with this size!'
                else:
                    accepted = ','.join(v for v in accepted)
                self.message.setText('Enumerate sentences with size: '+str(n)+'\n'+accepted)
                self.message.show()
            except ValueError as error:
                QMessageBox.critical(self, 'Error', error.args[0])

    def check_string(self):
        string = self.checkStringInput.text()
        accepted = self._automata.membership(string)
        if accepted:
            self.message.setText('The string is accepted by the automaton!')
            self.message.show()
        else:
            self.message.setText('The string is NOT accepted by the automaton!')
            self.message.show()

    def update_automata(self, row, col):
        table_item = self.transitionTable.item(row, col)
        text = table_item.text().replace(' ', '')
        states = sorted(self._automata.states)
        symbols = sorted(self._automata.symbols)
        if text != '-':
            if re.fullmatch(STATE_INPUT, text) is None:
                table_item.setText(self._table_data)
                self.message.setText('The states have to be a \'q\' followed by a number or a \'-\'')
                self.message.show()
            else:
                end_states = set(text.split(','))
                try:
                    self._automata.add_transition(states[row], symbols[col], end_states)
                except ValueError as error:
                    self.transitionTable.cellChanged.disconnect(self.update_automata)
                    table_item.setText(self._table_data)
                    self.transitionTable.cellChanged.connect(self.update_automata)
                    QMessageBox.critical(self, 'Error', error.args[0])
        else:
            self._automata.add_transition(states[row], symbols[col], set())

    def table_item_clicked(self, item):
        self.transitionTable.cellChanged.disconnect(self.update_automata)
        self._table_data = item.text()
        self.transitionTable.cellChanged.connect(self.update_automata)

    def table_item_double_clicked(self, item):
        self.transitionTable.cellChanged.disconnect(self.update_automata)
        item.setText(self._table_data)
        self.transitionTable.cellChanged.connect(self.update_automata)

    def update_transition_table(self):
        self.transitionTable.cellChanged.disconnect(self.update_automata)

        states = []
        for state in sorted(self._automata.states):
            preffix = ''
            if state == self._automata.initial_state:
                preffix += '->'
            if state in self._automata.final_states:
                preffix += '*'
            states.append(preffix + state)

        self.transitionTable.setRowCount(len(states))
        self.transitionTable.setVerticalHeaderLabels(states)

        self.transitionTable.setColumnCount(len(self._automata.symbols))
        self.transitionTable.setHorizontalHeaderLabels(sorted(self._automata.symbols))

        for i, state in enumerate(sorted(self._automata.states)):
            for j, symbol in enumerate(sorted(self._automata.symbols)):
                if (state, symbol) in self._automata.transitions:
                    item = ','.join(sorted(self._automata.transitions[state, symbol]))
                else:
                    item = '-'
                self.transitionTable.setItem(i, j, QTableWidgetItem(item))

        self.transitionTable.cellChanged.connect(self.update_automata)

    def validate_regular_grammar(self, grammar):
        first = True
        for k, v in grammar.productions.items():
            text = k + '->'
            for p in v:
                text += p + '|'
            if first:
                if re.fullmatch(INITIAL_GRAMMAR, text[:-1]) is None:
                    return False
                else:
                    first = False
            else:
                if re.fullmatch(GRAMMAR_INPUT, text[:-1]) is None:
                    return False

        return True

    def import_grammar(self):
        path, _ = QFileDialog.getOpenFileName(self)
        if path:
            try:
                grammar = Grammar()
                grammar.load(path)
                if self.validate_regular_grammar(grammar):
                    self._grammar = grammar
                    self.update_grammar_list()
                else:
                    QMessageBox.critical(self, 'Error', 'Not a regular grammar')

            except ValueError as error:
                QMessageBox.critical(self, 'Error', error.args[0])

    def export_grammar(self):
        path, _ = QFileDialog.getSaveFileName(self)
        if path:
            self._grammar.save(path)

    def convert_grammar(self):
        self.add_automata_to_list()
        self._automata = self._grammar.convert_to_automata()
        self._automata.determinize()
        self._automata.rename_states()
        self.update_transition_table()

    def add_production(self):
        keys = self._grammar.productions.keys()
        if self.productionList.count() == 0:
            text, ok = QInputDialog.getText(
                self, 'Add Initial Production', 'Input a production '+
                      'e.g(A -> aA | bB)')

            if ok:
                text = text.strip().replace(' ', '')
                while re.fullmatch(INITIAL_GRAMMAR, text) is None:
                    text, ok = QInputDialog.getText(self, 'Add Initial Production',
                        'Production not regular!')
                    if ok:
                        text = text.strip().replace(' ', '')

                self.productionList.addItem(text)
                key, set_values = text.split('->')
                self._grammar.add(key, set(set_values.split('|')))

        else:
            text, ok = QInputDialog.getText(
                self, 'Add Production', 'Input a production '+
                      'e.g(A -> aA | bB)')

            if ok:
                text = text.strip().replace(' ', '')
                while re.fullmatch(GRAMMAR_INPUT, text) is None:
                    text, ok = QInputDialog.getText(self, 'Add Production',
                        'Production not regular!')
                    if ok:
                        text = text.strip().replace(' ', '')

                key, set_values = text.split('->')
                if key not in keys:
                    self.productionList.addItem(text)
                    self._grammar.add(key, set(set_values.split('|')))
                else:
                    self.message.setText('This non terminal symbol already exists!')
                    self.message.show()

    def remove_production(self):
        for item in self.productionList.selectedItems():
            key = item.text().split('->')[0]
            self._grammar.remove(key)
            self.productionList.takeItem(self.productionList.row(item))

    def grammar_item_clicked(self, item):
        self.productionList.itemChanged.disconnect(self.update_grammar)
        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
        self._item_data=item.text()
        self.productionList.itemChanged.connect(self.update_grammar)

    def grammar_item_double_clicked(self, item):
        self.productionList.itemChanged.disconnect(self.update_grammar)
        item.setText(self._item_data)
        self.productionList.itemChanged.connect(self.update_grammar)

    def update_grammar(self, item):
        self.productionList.itemChanged.disconnect(self.update_grammar)
        keys = self._grammar.productions.keys()
        if self.productionList.indexFromItem(item).row() == 0:
            if re.fullmatch(INITIAL_GRAMMAR, item.text()) is None:
                item.setText(self._item_data)
                self.message.setText('Production not Regular!')
                self.message.show()
            else:
                key, set_values = item.text().split('->')
                old_key = self._item_data.split('->')[0]
                if key not in keys or key == old_key :
                    self._grammar.edit_key(old_key, key, set(set_values.split('|')))
                else:
                    item.setText(self._item_data)
                    self.message.setText('This non terminal symbol already exists!')
                    self.message.show()

        else:
            if re.fullmatch(GRAMMAR_INPUT, item.text()) is None:
                item.setText(self._item_data)
                self.message.setText('Production not Regular!')
                self.message.show()
            else:
                key, set_values = item.text().split('->')
                old_key = self._item_data.split('->')[0]
                if key not in keys or key == old_key :
                    self._grammar.edit_key(old_key, key, set(set_values.split('|')))
                else:
                    item.setText(self._item_data)
                    self.message.setText('This non terminal symbol already exists!')
                    self.message.show()

        self.productionList.itemChanged.connect(self.update_grammar)

    def update_grammar_list(self):
        self.productionList.clear()
        for k, v in self._grammar.productions.items():
            if v == set():
                continue
            text = k + '->'
            for p in v:
                text += p + '|'
            self.productionList.addItem(text[:-1])
