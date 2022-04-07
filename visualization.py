import re
import meshio
import random
import pandas as pd
import plotly.express as px
import pyvista
from pprint import pprint

# mesh = examples.download_notch_stress()
# mesh.plot(scalars='Nodal Stress', component=0, cmap='turbo', cpos='xy')


def parse_dat_file(_file):
    with open(_file, 'r') as f:
        _str = f.read()

    _beg = _str.find('CONNECT')
    _end = _str.find('MATERIAL 1')

    df_str = _str[_beg + len('CONNECT'):_end]
    df_str = df_str.replace('\n\t\t\t', ' ')
    df_str_clean = re.sub('\n\s{4,}', ' ', df_str)
    df_list = [re.split('\s+', line.strip()) for line in df_str_clean.split('\n') if re.split('\s+', line.strip())[0]]

    _df = pd.DataFrame(df_list)
    return _df


def get_ordered_nodes_per_cell(_df_all, list_of_all_nodes):
    cells_nodes = []
    for node_list in list_of_all_nodes:
        _df = _df_all.loc[node_list, ['X', 'Y', 'Z']]
        cells_nodes.append(sort_hex20_according_to_pyvista(_df))
    return cells_nodes


def sort_hex20_according_to_pyvista(_df):
    """ dataframe consisting  3 columns (X, Y, Z) and 20 indices corresponidng to nodes
    pyvista has order 0-3 outer nodes of bottom; 4-7 outer nodes top; 8-11 middle nodes bottom;
    12-15 - middle nodes top; 16-19 - middle nodes in middle"""

    # idx = _df.sort_values(['X', 'Y', 'Z']).index

    x_min = _df['X'].min()
    x_max = _df['X'].max()
    x_mid = _df.loc[~_df['X'].isin([x_min, x_max]), 'X'].values[0]

    y_min = _df['Y'].min()
    y_max = _df['Y'].max()
    y_mid = _df.loc[~_df['Y'].isin([y_min, y_max]), 'Y'].values[0]

    z_min = _df['Z'].min()
    z_max = _df['Z'].max()
    z_mid = _df.loc[~_df['Z'].isin([z_min, z_max]), 'Z'].values[0]

    idx = [0 for i in range(20)]

    idx[0] = _df.loc[(_df['Z'] == z_min) & (_df['X'] == x_min) & (_df['Y'] == y_min)].index[0]
    idx[1] = _df.loc[(_df['Z'] == z_min) & (_df['X'] == x_max) & (_df['Y'] == y_min)].index[0]
    idx[2] = _df.loc[(_df['Z'] == z_min) & (_df['X'] == x_max) & (_df['Y'] == y_max)].index[0]
    idx[3] = _df.loc[(_df['Z'] == z_min) & (_df['X'] == x_min) & (_df['Y'] == y_max)].index[0]

    idx[4] = _df.loc[(_df['Z'] == z_max) & (_df['X'] == x_min) & (_df['Y'] == y_min)].index[0]
    idx[5] = _df.loc[(_df['Z'] == z_max) & (_df['X'] == x_max) & (_df['Y'] == y_min)].index[0]
    idx[6] = _df.loc[(_df['Z'] == z_max) & (_df['X'] == x_max) & (_df['Y'] == y_max)].index[0]
    idx[7] = _df.loc[(_df['Z'] == z_max) & (_df['X'] == x_min) & (_df['Y'] == y_max)].index[0]

    idx[8] = _df.loc[(_df['Z'] == z_min) & (_df['X'] == x_mid) & (_df['Y'] == y_min)].index[0]
    idx[9] = _df.loc[(_df['Z'] == z_min) & (_df['X'] == x_max) & (_df['Y'] == y_mid)].index[0]
    idx[10] = _df.loc[(_df['Z'] == z_min) & (_df['X'] == x_mid) & (_df['Y'] == y_max)].index[0]
    idx[11] = _df.loc[(_df['Z'] == z_min) & (_df['X'] == x_min) & (_df['Y'] == y_mid)].index[0]

    idx[12] = _df.loc[(_df['Z'] == z_max) & (_df['X'] == x_mid) & (_df['Y'] == y_min)].index[0]
    idx[13] = _df.loc[(_df['Z'] == z_max) & (_df['X'] == x_max) & (_df['Y'] == y_mid)].index[0]
    idx[14] = _df.loc[(_df['Z'] == z_max) & (_df['X'] == x_mid) & (_df['Y'] == y_max)].index[0]
    idx[15] = _df.loc[(_df['Z'] == z_max) & (_df['X'] == x_min) & (_df['Y'] == y_mid)].index[0]

    idx[16] = _df.loc[(_df['Z'] == z_mid) & (_df['X'] == x_min) & (_df['Y'] == y_min)].index[0]
    idx[17] = _df.loc[(_df['Z'] == z_mid) & (_df['X'] == x_max) & (_df['Y'] == y_min)].index[0]
    idx[18] = _df.loc[(_df['Z'] == z_mid) & (_df['X'] == x_max) & (_df['Y'] == y_max)].index[0]
    idx[19] = _df.loc[(_df['Z'] == z_mid) & (_df['X'] == x_min) & (_df['Y'] == y_max)].index[0]

    return [x-1 for x in _df.loc[idx, ['X', 'Y', 'Z']].index.tolist()]


if __name__ == '__main__':
    csv_file = r'C:\Users\mwozniak\OneDrive - BESIX\Desktop\Tour Triangle\fire\lin files\PTE003.csv'
    df = pd.read_csv(csv_file, skiprows=1)
    df.drop([0], inplace=True)
    df = df.astype({col: float for col in ['X', 'Y', 'Z', 'PTE']})
    points = df[['X', 'Y', 'Z']].values.tolist()

    # print(df)
    # df = df.astype({col: float for col in ['X', 'Y', 'Z', 'PTE']})
    # fig = px.scatter_3d(x=df['X'], y=df['Y'], z=df['Z'], color=df['PTE'])
    # fig.show()

    dat_file = r'C:\Users\mwozniak\OneDrive - BESIX\Desktop\Tour Triangle\fire\lin files\Triangle fire beam00.dat'
    df1 = parse_dat_file(dat_file)
    df1 = df1.loc[:, df1.columns]
    df1 = df1.astype({col: int for col in range(2, 22)})

    cells_node_unordered = df1[[a for a in range(2, 22)]].values.tolist()
    cells_node_ordered = get_ordered_nodes_per_cell(df, cells_node_unordered)
    cells = [('hexahedron20', cells_node_ordered)]
    point_data = {'temp': df['PTE'].values.tolist()}

    mesh = meshio.Mesh(points, cells, point_data=point_data)

    mesh.write('pupa.vtk')

    mesh_pv = pyvista.read('pupa.vtk')
    mesh_pv.plot(scalars='temp', show_edges=False, cmap='turbo')
