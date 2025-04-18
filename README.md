# dev-auto
development automation

## mk-excel-db.py
### 목적
* mysql table 을 조회해서 schema 엑셀 문서로 만든다
### 사용법
python mk-excel-db.py table1 table2 ...

## get-col
### 목적
* 한글단어를 영문단어로 바꾼다
* 보기 : 주민등록번호 -> RSDR_REG_NO
### build
pyinstaller --onefile --noconsole --add-data "word.txt;." get_column_gui_mecab3.py

### tree
$ tree get-col
get-col
|-- get_column_gui_mecab3.py
|-- mecab
|   |-- bin
|   |-- etc
|   |   `-- mecabrc
|   |-- include
|   |   `-- mecab.h
|   |-- lib
|   `-- share
`-- word.txt

### mecab download
* confer https://haseong8012.tistory.com/51
