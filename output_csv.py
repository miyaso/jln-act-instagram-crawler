# -*- coding: utf-8 -*-
import pandas as pd

pickle_file = 'dump/asobi_instagram_like.pickle'
output_file = 'output/jln_activity_instagram_result.csv'
columns = ['date', 'userName', 'comment', 'pictureUrl', 'like']

def main():
    df = pd.read_pickle(pickle_file)
    df['comment'] = df['comment'].map(lambda x: x.replace('\n', ' '))
    encodeSeries(df, columns)
    df.to_csv(output_file, 
                    index=False,
                    columns=columns,
                    encoding="utf-8")

def encodeSeries(df, columns):
    for c in columns:
        df[c] = df[c].map(lambda x: x.encode('utf-8') 
                                        if isinstance(x, unicode) else x)

if __name__ == '__main__':
    main()
