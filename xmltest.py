import xml.etree.ElementTree as et
from xml.dom import minidom
import sys
from PySide import QtGui, QtCore
from functools import partial

def prettifyXml(elem):
    rough_string = et.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")
		
class CommentWidget(QtGui.QTextEdit) :
	def __init__ (self, tokens) :
		super(self.__class__, self).__init__()
		self.tokens = tokens
		self.setGeometry(0, 0, 500, 100)
		self.initUI()
		self.mouse = None
		self.eventPos = None
	def initUI(self) :
		self.layout = QtGui.QVBoxLayout()
		self.setReadOnly(True)
		self.doc = QtGui.QTextDocument()
		self.setDocument(self.doc)
	def getAction(self, label, callback, parent) :
		action = QtGui.QAction(label, parent)
		action.triggered.connect(partial(callback))
		return action
	def onEditableAction(self) :
		self.setReadOnly(False)
	def onLockAction(self) :
		self.setReadOnly(True)
	def onSaveAction(self) :
		mbox = QtGui.QMessageBox()
		mbox.setText('Comments Saved.')
		mbox.exec_()
	def updateComment(self, path) :
		tree = et.parse(path)
		root = tree.getroot()
		elem = root.find('comment')
		if elem.text != '' :
			self.doc.setPlainText(elem.text.strip())
	def mousePressEvent(self, event) :
		self.mouse = event.button()
		self.eventPos = event.globalPos()
		super(self.__class__, self).mousePressEvent(event)
		if self.mouse == QtCore.Qt.MouseButton.RightButton :
			menu = QtGui.QMenu(self)
			if self.isReadOnly() :
				menu.addAction(self.getAction(u'Make Editable', self.onEditableAction, self))
			else :
				menu.addAction(self.getAction(u'Make Non-Editable', self.onLockAction, self))
				menu.addAction(self.getAction(u'Save Comment', self.onSaveAction, self))	
			menu.exec_(self.eventPos)
	
def createBlankXml() :
	root = et.Element('shader')
	comment = et.SubElement(root, 'comment')
	comment.text = 'this is a comment.'
	et.dump(root)
	path = 'Z:/marza/proj/kibble/users/ArakawaT/temp/test.xml'
	#open(path, 'w').write(prettifyXml(root))
	return root

if __name__ == '__main__' :
	tree = createBlankXml()
	path = 'Z:/marza/proj/kibble/users/ArakawaT/temp/test.xml'
	tokens = []
	app = QtGui.QApplication(sys.argv)
	window = CommentWidget(tokens)
	window.updateComment(path)
	window.setWindowTitle('Comment Editor')
	window.show()
	sys.exit(app.exec_())
	