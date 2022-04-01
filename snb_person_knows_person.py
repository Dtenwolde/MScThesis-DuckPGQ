import pandas as pd
import warnings
import os
warnings.filterwarnings("ignore")

all_sf = ['sf0.1', 'sf1', 'sf3', 'sf10', 'sf30'] #
fractions = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]

#%%
for sf in all_sf: 
    print(f"Starting {sf}")
    for fraction in fractions:
        print(f"Starting {fraction}")
        df = pd.read_csv(f'/data/lsqb/data/social-network-{sf}-projected-fk/Person_knows_Person.csv', delimiter='|')

        df.rename(columns={':START_ID(Person)':'source',':END_ID(Person)':'target'}, inplace=True)
        running_sum = 0
        running_length = 0
        df_grouped = df.groupby('source')
        df_trimmed = pd.DataFrame(columns=['source', 'target'])

        for name, group in df_grouped:
            # Change this for the number of connections
            if fraction != 1:
                num_of_knows = int(len(group) * fraction)
                trimmed = group.sample(num_of_knows, replace=True).drop_duplicates()
                running_sum += num_of_knows
            else:
                trimmed = group
                running_sum += len(group)
            running_length += 1
            # if file does not exist write header
            if not os.path.isfile(f"input_files/person_knows_person_trimmed_{sf}_{fraction}.csv"):
               trimmed.to_csv(f"input_files/person_knows_person_trimmed_{sf}_{fraction}.csv", header=True, index=False)
            else: # else it exists so append without writing the header
               trimmed.to_csv(f"input_files/person_knows_person_trimmed_{sf}_{fraction}.csv", mode='a', header=False, index=False)

        final_df = pd.read_csv(f"input_files/person_knows_person_trimmed_{sf}_{fraction}.csv")
        os.remove(f"input_files/person_knows_person_trimmed_{sf}_{fraction}.csv")
        final_df.to_csv(f"input_files/person_knows_person_trimmed_{sf}_{fraction}_{int(round(running_sum/running_length))}.csv", index=False)
