from PyQt6.QtWidgets import QListWidget
from PyQt6.QtCore import Qt

class SelectableListWidget(QListWidget):
    def __init__(self, items, parent=None):
        super().__init__(parent)
        self.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.addItem('Select All')  # Add 'Select All' item at the top
        for item in items:
            self.addItem(item)
        self.itemClicked.connect(self.handle_item_clicked)

    def handle_item_clicked(self, item):
        if item.text() == 'Select All':
            if item.isSelected():
                self.selectAll()
            else:
                self.clearSelection()
        else:
            select_all_item = self.item(0)  # 'Select All' is the first item
            all_selected = all(self.item(i).isSelected() for i in range(1, self.count()))
            select_all_item.setSelected(all_selected)

    def select_all_items(self):
        '''Check all items except 'Select All' itself (if desired).'''
        for i in range(1, self.model().rowCount()):
            it = self.model().item(i)
            it.setCheckState(Qt.CheckState.Checked)

    def deselect_all_items(self):
        '''Uncheck all items except 'Select All' itself (if desired).'''
        for i in range(1, self.model().rowCount()):
            it = self.model().item(i)
            it.setCheckState(Qt.CheckState.Unchecked)

    def checkedItems(self):
        '''Return a list of text for all items that are checked (excluding 'Select All').'''
        selected = []
        # Start from 1 if the 0th item is 'Select All'
        for i in range(1, self.model().rowCount()):
            item = self.model().item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected.append(item.text())
        return selected
