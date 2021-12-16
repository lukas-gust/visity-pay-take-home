import re
import csv
import logging

from os import listdir, makedirs
from os.path import isfile, join, exists, basename
from datetime import datetime
import sqlite3 as db



data_dir = './data'
checkpoint_dir = './data/checkpoint'

class VisitPayFile:
    def __init__(self, path):
        self.path = path
        self.file_name = basename(path)
        self.hospital, _, self.ftype, self.date, self.time = str.split(self.file_name, '.')[0].split('_')
        self.datetime = datetime.strptime('_'.join([self.date, self.time]), '%Y%m%d_%H%M%S')
        self.delimiter = '\t'

    def __str__(self):
        return 'Path: {}, Type: {}, datetime: {}'.format(self.path, self.ftype, self.datetime)
        

def filter_data_files(file_list, checkpoints):
    checkpoints = filter(lambda c: re.match('^\d{8}_\d{6}', c), checkpoints) # can be improved to filter out bad dates
    checkpoints = list(map(lambda c: datetime.strptime(c, '%Y%m%d_%H%M%S'), checkpoints)) # this is a good piece to test

    max_checkpoint = datetime.strptime('20211201_131916', '%Y%m%d_%H%M%S') # max(checkpoints)

    return list(filter(lambda f: f.datetime > max_checkpoint, file_list))

if __name__ == '__main__':
    logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

    types = ['Procedure', 'Visit', 'Transaction']

    file_list = [VisitPayFile(join(data_dir, f)) for f in listdir(data_dir) if isfile(join(data_dir, f))]

    if exists(checkpoint_dir): # filter files by datefrom checkpoint to now
        checkpoints = listdir(checkpoint_dir)
        checkpoints = filter(lambda c: re.match('^\d{8}_\d{6}', c), checkpoints) # can be improved to filter out bad dates
        checkpoints = list(map(lambda c: datetime.strptime(c, '%Y%m%d_%H%M%S'), checkpoints)) # this is a good piece to test

        max_checkpoint = datetime.strptime('20211201_131916', '%Y%m%d_%H%M%S') # max(checkpoints)

        file_list = list(filter(lambda f: f.datetime > max_checkpoint, file_list))

        # no files?
    
    conn = db.connect('./visitpay-database.db')
    conn.execute('''PRAGMA foreign_keys = ON;''')
    for ftype in types: # for each file type
        files = filter(lambda f: f.ftype == ftype, file_list)
        files = sorted(files, key= lambda o: o.datetime)

        for file in files:
            with open(file.path) as csvfile:
                reader = csv.reader(csvfile, delimiter=file.delimiter)

                cols = reader.__next__()
                str_cols = ','.join(['`' + col + '`' for col in cols])
                col_num = len(cols)
                place_holders = ','.join(['?']*col_num)
                insert_sql = 'INSERT INTO `{}` ({}) VALUES ({})'.format(ftype, str_cols, place_holders) # possible injection point, but this isn't user facing.
                # implement psert capability or assume its append only

                data = [tuple(row) for row in reader]
                try:
                    conn.executemany(insert_sql, data)
                    conn.commit()

                    logging.info('Changes committed.')
                except db.IntegrityError as e:
                    print(e)

                    logging.warning(str(e) + insert_sql)

    conn.close()
    
    checkpoint_datetime = datetime.now().strftime('%Y%m%d_%H%M%S')
    if not exists(checkpoint_dir) : makedirs(checkpoint_dir)
    open(join(checkpoint_dir, checkpoint_datetime), 'a').close() # make checkpoint after success
    logging.info('Checkpoint saved at {}.'.format(checkpoint_datetime))
