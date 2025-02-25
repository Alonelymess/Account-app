import pandas as pd

class DataHandle:
    def __init__(self):
        self.path = 'source/test.csv'
        self.df = self.read()
        
    def read(self):
        df = pd.read_csv(self.path)
        df["Ngày"] = pd.to_datetime(df['Ngày'], dayfirst=False)
        try:
            df["Giá trị"] = df["Giá trị"].apply(lambda x: float(x.replace(',', '.')))
        except:
            pass
        try:
            df["Each"] = df["Each"].apply(lambda x: float(x.replace(',', '.')))
        except:
            pass
        return df
    
    def append(self, data):
        df = pd.concat([self.df, data])
        return df
    
    def delete(self, index):
        df = self.df.drop(index)        
        return df
        
    def update(self, index, data):
        self.df.loc[index] = data
        
        return self.df
    
    def get(self, index):
        df = pd.read_csv(self.path)
        return df.loc[index]
    

    

# if __name__ == '__main__':
#     print(read())