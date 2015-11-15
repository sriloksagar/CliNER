#database.py creates a .db file for performing umls searches.
import sqlite3
import os
import sys
import os

features_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if features_dir not in sys.path:
    sys.path.append(features_dir)


# find where umls tables are located
from read_config import enabled_modules
enabled = enabled_modules()
umls_tables = enabled['UMLS']



def create_db():

    print "\ncreating umls.db"
    #connect to the .db file we are creating.
    db_path = os.path.join(umls_tables, 'umls.db')
    conn = sqlite3.connect( db_path )
    conn.text_factory = str

    print "opening files"
    #load data in files.
    try:
        mrsty_path = os.path.join(umls_tables, 'MRSTY.RRF')
        MRSTY_TABLE_FILE = open( mrsty_path, "r" )
    except IOError:
        print "\nNo file to use for creating MRSTY.RRF table\n"
        conn.close()
        sys.exit()

    try:
        mrcon_path = os.path.join(umls_tables, 'MRCONSO.RRF')
        MRCON_TABLE_FILE = open( mrcon_path , "r" )
    except IOError:
        print "\nNo file to use for creating MRCONSO.RRF table\n"
        conn.close()
        sys.exit()

    try:
        mrrel_path = os.path.join(umls_tables, 'MRREL.RRF')
        MRREL_TABLE_FILE = open( mrrel_path , "r" )
    except IOError:
        print "\nNo file to use for creating MRREL.RRF table\n"
        conn.close()
        sys.exit()

    print "creating tables"
    c = conn.cursor()

    #create tables.
    c.execute( "CREATE TABLE MRSTY( CUI, TUI, STN, STY, ATUI, CVF  ) ;" )
    c.execute( "CREATE TABLE MRCON( CUI, LAT, TS, LUI, STT, SUI, ISPREF, AUI, SAUI, SCUI, SDUI, SAB, TTY, CODE, STR, SRL, SUPPRESS, CVF ) ;" )
    c.execute( "CREATE TABLE MRREL( CUI1, AUI1, STYPE1, REL, CUI2, AUI2, STYPE2, RELA, RUI, SRUI, SAB, SL, RG, DIR, SUPPRESS, CVF );")

    print "inserting data into MRSTY table"
    for line in MRSTY_TABLE_FILE:

        line = line.strip('\n')

        assert line[-1] == '|', "str: {}, char: ".format(line, line[-1])

        line = line.split('|')

        # end will always be empty str
        line.pop()

        assert len(line) == 6

        c.execute( "INSERT INTO MRSTY( CUI, TUI, STN, STY, ATUI, CVF ) values( ?, ?, ?, ?, ?, ?)" , tuple(line))

    MRSTY_TABLE_FILE.close()

    print "inserting data into MRCON table"
    for line in MRCON_TABLE_FILE:

        line = line.strip('\n')

        assert line[-1] == '|', "str: {}, char: ".format(line, line[-1])

        line = line.split('|')

        # end will always be empty str
        line.pop()

        assert len(line) == 18

        c.execute( "INSERT INTO MRCON( CUI, LAT, TS, LUI, STT, SUI, ISPREF, AUI, SAUI, SCUI, SDUI, SAB, TTY, CODE, STR, SRL, SUPPRESS, CVF ) values ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", tuple(line))

    MRCON_TABLE_FILE.close()

    print "inserting data into MRREL table"
    for line in MRREL_TABLE_FILE:

        line = line.strip('\n')

        assert line[-1] == '|', "str: {}, char: ".format(line, line[-1])

        line = line.split('|')

        # end will always be empty str
        line.pop()

        assert len(line) == 16

        c.execute( "INSERT INTO MRREL(  CUI1, AUI1, STYPE1, REL, CUI2, AUI2, STYPE2, RELA, RUI, SRUI, SAB, SL, RG, DIR, SUPPRESS, CVF ) values( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? )" , tuple(line))

    MRREL_TABLE_FILE.close()

    print "creating indices"

    #create indices for faster queries
    c.execute( "CREATE INDEX mrsty_cui_map ON MRSTY(CUI)")
    c.execute( "CREATE INDEX mrcon_str_map ON MRCON(STR)")
    c.execute( "CREATE INDEX mrcon_cui_map ON MRCON(CUI)")
    c.execute( "CREATE INDEX mrrel_cui2_map ON MRREL( CUI2 )" )
    c.execute( "CREATE INDEX mrrel_cui1_map on MRREL( CUI1 ) " )
    c.execute( "CREATE INDEX mrrel_rel_map on MRREL( REL )" )

    #save changes to .db
    conn.commit()

    print "\nsqlite database created"

    #close connection
    conn.close()

if __name__ == "__main__":
    create_db()

