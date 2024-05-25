import pandas as pd
import time

data = {'shoulder_center' : [], 'shoulder_right' : [], 'shoulder_left' : [], 'center_height' : [], 'right_height' : [], 'left_height' : []}
df = pd.DataFrame(data)

auto_flag = input("Please input auto("A") : ")

for i in range(1, 10):
  count += 1
  current_time = 0

  df = df._append({'time': current_time, 'data': count}, ignore_index=True)
  

df.to_excel('ex_data.xlsx', index=False)
