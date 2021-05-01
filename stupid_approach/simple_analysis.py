from strYa.posture_position import Buffer

buf = pp.Buffer()

def plot_buf_from_file(buf: pp.Buffer, file_name: str, idx: int = 0) -> None:
    df = pd.DataFrame(buf.from_file(file_name))
    
    columns_mean: Dict[int, int] = {}
    for column in df.columns:
        columns_mean[column] = df[column].mean()
        
    for column in columns_mean:
        df[column] = df[column].apply(lambda x: x - columns_mean[column])
        
    pd.set_option('display.max_rows', 100)
    line1, line2 = df[idx].to_list(), [df[0].mean() for elm in df[idx]]
    # print(line1, line2)
    line3 = [(columns_mean[0] + line2[0])/4 for elm in line2]
    # print(line3)
    
    plt.plot(line1)
    plt.plot(line2)
    plt.plot(line3)
