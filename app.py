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
    """
    Represents a file and its metadata read from the landing location.
    """
    def __init__(self, path):
        self.path = path
        self.file_name = basename(path)
        self.hospital, _, self.ftype, self.date, self.time = str.split(self.file_name, '.')[0].split('_')
        self.datetime = datetime.strptime('_'.join([self.date, self.time]), '%Y%m%d_%H%M%S')
        self.delimiter = '\t'

    def __str__(self):
        return 'Path: {}, Type: {}, datetime: {}'.format(self.path, self.ftype, self.datetime)

def filter_files_by_type(files, ftype):
    files = filter(lambda f: f.ftype == ftype, file_list)
    files = sorted(files, key= lambda o: o.datetime)

    return files

def filter_checkpoints(checkpoint_dir):
    checkpoints = listdir(checkpoint_dir)
    checkpoints = filter(lambda c: re.match('^\d{8}_\d{6}', c), checkpoints) # can be improved to filter out bad dates
    checkpoints = list(map(lambda c: datetime.strptime(c, '%Y%m%d_%H%M%S'), checkpoints)) # this is a good piece to test

    return checkpoints

if __name__ == '__main__':
    logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

    types = ['Procedure', 'Visit', 'Transaction'] # this could be dynamic based on db

    file_list = [VisitPayFile(join(data_dir, f)) for f in listdir(data_dir) if isfile(join(data_dir, f))]

    if exists(checkpoint_dir): # filter files by datetime from checkpoint to now
        checkpoints = filter_checkpoints(checkpoint_dir)

        max_checkpoint = max(checkpoints)

        file_list = list(filter(lambda f: f.datetime > max_checkpoint, file_list))

        if not file_list: 
            logging.info('No files to process after {}. Exiting.'.format(max_checkpoint))
            exit()

    logging.info('Processing {} files.'.format(len(file_list)))

    new_checkpoint = max(file_list, key=lambda f: f.datetime).datetime
    
    conn = db.connect('./visitpay-database.db')
    conn.execute('''PRAGMA foreign_keys = ON;''') # enforce key constraints for sqlite

    for ftype in types: # for each file type
        files = filter_files_by_type(file_list, ftype)

        for file in files:
            with open(file.path) as csvfile:
                reader = csv.reader(csvfile, delimiter=file.delimiter)

                cols = reader.__next__()
                str_cols = ','.join(['`' + col + '`' for col in cols]) # format column names
                place_holders = ','.join(['?']*len(cols))

                insert_sql = 'INSERT INTO `{}` ({}) VALUES ({}) ON CONFLICT DO NOTHING'.format(ftype, str_cols, place_holders) # possible injection vector at the column name level, but this isn't user facing.

                data = [tuple(row) for row in reader] # this could be refactored into a yield in case of large volume

                if len(cols) != min([len(d) for d in data]):
                    logging.error('Bad data file. Unable to parse correctly.')

                try:
                    conn.executemany(insert_sql, data)
                    conn.commit()

                    logging.info('Changes committed.')
                except db.IntegrityError as e:
                    print(e)

                    logging.warning(str(e) + insert_sql + file.path)

    conn.close()
    
    if not exists(checkpoint_dir) : makedirs(checkpoint_dir) # make the checkpoint directory if it doesn't exist

    checkpoint_datetime = new_checkpoint.strftime('%Y%m%d_%H%M%S')
    open(join(checkpoint_dir, checkpoint_datetime), 'a').close() # make checkpoint after success

    logging.info('Checkpoint saved at {}.'.format(checkpoint_datetime))
