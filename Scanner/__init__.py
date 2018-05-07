import re

from enum import Enum
from prettytable import PrettyTable

list_token = []

class TokenType(Enum):
	TAG_OPEN_SYMBOL = 0
	TAG_CLOSE_SYMBOL = 1
	TAG_ASSIGNMENT_SYMBOL = 2
	TAG_NAME = 3
	TAG_ATTRIBUTE_NAME = 4
	TAG_ATTRIBUTE_VALUE = 5
	TAG_IDENTIFIER = 6
	RAW_DATA = 7
	COMMENT_OPEN = 8
	COMMENT_CLOSE = 9
	ALPHABHET = 10

	ELEMENT = 11
	DIVIDER = 12

	DOCUMENT_TYPE = 13


class Token:
	def __init__(self,idx,string,tokentype):
		self.idx = idx
		self.html = string
		self.type = tokentype;


class TokenBuilder:

	re_document_type = re.compile("<!.* html>")
	re_comment_open = re.compile("\<!--")
	re_open_tag = re.compile("""(<)([a-z0-9]+)([a-zA-Z0-9 ='",.\-_:/]*?)(>)""")
	re_self_closing_tag = re.compile("""(<)([a-z0-9]+)([a-zA-Z0-9 ='",.\-_:/]*?)(\/>)""")
	re_raw_data = re.compile(">\w+<")
	re_close_tag = re.compile("""(</)([a-z0-9]+)(?!\/)(>)""")
	re_comment_close = re.compile("(.)*(-->)")
	re_raw_data2 = re.compile("[\w ,\/\.]+")

	def __init__(self,string,idx):
		self.tokens = []
		self.idx = idx

		result_document_type 	= self.find_until_end(self.re_document_type,string)
		result_comment_open 	= self.find_until_end(self.re_comment_open,string)
		result_comment_close 	= self.find_until_end(self.re_comment_close,string)
		result_open_tag 		= self.find_until_end(self.re_open_tag,string)
		result_close_tag 		= self.find_until_end(self.re_close_tag,string)
		result_self_closing_tag = self.find_until_end(self.re_self_closing_tag,string)
		result_raw_data 		= self.find_until_end(self.re_raw_data,string)

		if(result_comment_open == [] and
			result_comment_close == [] and
			result_open_tag == [] and
			result_close_tag == [] and
			result_self_closing_tag == [] and
			result_raw_data == [] and
			result_document_type == []) :

			result_raw_data2		= self.find_until_end(self.re_raw_data2,string)
		else :
			result_raw_data2		= []

		self.tokenize(result_document_type,'document_type')
		self.tokenize(result_comment_open,'comment_open')
		self.tokenize(result_open_tag,'open_tag')
		self.tokenize(result_self_closing_tag,'self_closing_tag')
		self.tokenize(result_raw_data,'raw_data')
		self.tokenize(result_raw_data2,'raw_data2')
		self.tokenize(result_close_tag,'close_tag')
		self.tokenize(result_comment_close,'comment_close')

		global list_token
		list_token.append(self.tokens)

	def find_until_end(self,regex,string):
		return regex.findall(string)

	def tokenize(self,results,tipe):
		if tipe == 'comment_open' and results != []:
			self.tokens.append(Token(self.idx,'== COMMENT OPEN ==',TokenType.ELEMENT))
		if tipe == 'open_tag' and results != [] : 
			self.tokens.append(Token(self.idx,'== OPENING TAG ==',TokenType.ELEMENT))
		if tipe == 'self_closing_tag' and results != [] :
			self.tokens.append(Token(self.idx,'== SELF CLOSING TAG ==',TokenType.ELEMENT))
		if tipe == 'close_tag' and results != [] :
			self.tokens.append(Token(self.idx,'== CLOSING TAG ==',TokenType.ELEMENT))
		if tipe == 'comment_close' and results != [] :
			self.tokens.append(Token(self.idx,'== COMMENT CLOSE ==',TokenType.ELEMENT))
		if tipe == 'document_type' and results != [] :
			self.tokens.append(Token(self.idx,'== DOCUMENT TYPE ==',TokenType.ELEMENT))
		for result in results:
			if result == None : return
			if tipe == 'comment_open':
				self.tokens.append(Token(self.idx,''.join(map(str,result)),TokenType.COMMENT_OPEN))
			if tipe == 'open_tag' or tipe == 'self_closing_tag':
				res = ''.join(map(str,result))
				if(res == '/') and tipe != 'self_closing_tag':
					continue
				self.tokens.append(Token(self.idx,result[0],TokenType.TAG_OPEN_SYMBOL))
				tag_name = result[1]
				self.tokens.append(Token(self.idx,tag_name,TokenType.TAG_NAME))
				attribute = self.parse_attr(result[2])
				for attr in attribute:
					if '=' in attr:
						attr = attr.split('=')
						self.tokens.append(Token(self.idx,attr[0],TokenType.TAG_ATTRIBUTE_NAME))
						self.tokens.append(Token(self.idx,'=',TokenType.TAG_ASSIGNMENT_SYMBOL))
						self.tokens.append(Token(self.idx,attr[1],TokenType.TAG_ATTRIBUTE_VALUE))
					else :
						attr = attr.strip()
						if attr != "" : 
							self.tokens.append(Token(self.idx,attr,TokenType.TAG_IDENTIFIER))

				self.tokens.append(Token(self.idx,result[3],TokenType.TAG_CLOSE_SYMBOL))
			if tipe == 'raw_data' :
				self.tokens.append(Token(self.idx,''.join(map(str,result))[1:-1],TokenType.RAW_DATA))
			if tipe == 'raw_data2' :
				self.tokens.append(Token(self.idx,''.join(map(str,result)),TokenType.RAW_DATA))
			if tipe == 'close_tag' :
				self.tokens.append(Token(self.idx,result[0],TokenType.TAG_OPEN_SYMBOL))
				self.tokens.append(Token(self.idx,result[1],TokenType.TAG_NAME))
				self.tokens.append(Token(self.idx,result[2],TokenType.TAG_CLOSE_SYMBOL))
			if tipe == 'comment_close':
				self.tokens.append(Token(self.idx,result[1],TokenType.COMMENT_OPEN))
			if tipe == 'document_type':
				self.tokens.append(Token(self.idx,''.join(map(str,result)),TokenType.DOCUMENT_TYPE))
			self.tokens.append(Token(self.idx,'---',TokenType.DIVIDER))

	def parse_attr(self,string):
		list_attr = []
		count_quote = 0
		idx = 0
		while True :
			try :
				if string[idx] == ' ' and count_quote!=1:
					list_attr.append(string[idx])
					string = string[idx+1:]
					idx = 0
				if string[idx] == '"' or string[idx] == "'" : 
					count_quote+=1
				if count_quote == 2:
					list_attr.append(string[:idx+1])
					string = string[idx+1:]
					idx = 0
					count_quote = 0
			except IndexError :
				break
			idx+=1
		return list_attr


class LexicalAnalyzer:
	files = []

	def __init__(self,filename):
		idx = 0
		with open(filename,'r+') as f :
			for line in f :
				TokenBuilder(line,idx)
				self.files.append(line)
				idx+=1

	def print(self):
		global list_token
		curr_idx = 0
		
		for tokens in list_token:
			print(self.files[curr_idx],end='')
			x = PrettyTable(['Token','Token Type'])
			for tok in tokens:
				if(tok.type == TokenType.ELEMENT) :
					x.add_row([tok.html,'========'])
				elif(tok.type == TokenType.DIVIDER) :
					x.add_row([tok.html,'---'])
				else :
					x.add_row([tok.html,tok.type])
			print()
			print(x)
			print()
			curr_idx+=1
