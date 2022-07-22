import pandas as pd
import streamlit as st
from numpy import int32
# from streamlit_option_menu import option_menu

st.title('Vulnerability stats - Trends')

@st.experimental_memo(suppress_st_warning=True)
def upload_csv_files(csv_file):
    if not csv_files:
        st.warning('No csv files loaded, load files first ...') 
        return None, None, None
    else:
        with st.spinner("Please Wait ... "):
            ipstats  = pd.read_csv(csv_file, low_memory=False)
            ipstats.Low = ipstats.Low.fillna(0).astype(int32)
            ipstats['nvul'] = ipstats.High + ipstats.Medium + ipstats.Low + ipstats.Warning
            dts = sorted(ipstats.scan_month.unique())
            profile_groups = sorted(ipstats.profile_group.unique())

        # st.success(txt)
        return ipstats, dts, profile_groups
        
        

def convert_df (df):
    return df.to_csv().encode('utf-8')

def format_df(ipstats, dts, profiles):
    ipstats.Low = ipstats.Low.fillna(0).astype(int32)
    ipstats['nvul'] = ipstats.High + ipstats.Medium + ipstats.Low + ipstats.Warning

    stats = ipstats[['profile_group', 'scan_month', 'nvul', 'total_score']].groupby(['profile_group', 'scan_month']).sum()
    stats['host_count'] = ipstats[['profile_group', 'scan_month', 'ipaddress']].groupby(['profile_group', 'scan_month']).count()
    stats['nvul_per_host'] = stats.nvul/stats.host_count
    stats['nvul_per_host'] = stats.nvul_per_host.astype(int32)
    stats['vscore_per_host'] = stats.total_score/stats.host_count
    stats['vscore_per_host'] = stats.vscore_per_host.round(0)

    plt_stats = stats.reset_index()
    if dts: # there are values, filter out
        plt_stats = plt_stats[plt_stats.scan_month.isin(dts)]
    if profiles: # there are values, filter out
        plt_stats = plt_stats[plt_stats.profile_group.isin(profiles)]

    plt_per_host = plt_stats.pivot(index= 'scan_month', columns='profile_group', values='nvul_per_host').fillna(0).astype(int32)
    plt_host_count = plt_stats.pivot(index= 'scan_month', columns='profile_group', values='host_count').fillna(0).astype(int32)
    plt_vscore = plt_stats.pivot(index= 'scan_month', columns='profile_group', values='vscore_per_host').fillna(0).astype(int32)

    return plt_per_host, plt_host_count, plt_vscore

csv_files= st.file_uploader('Select ipstatsall.csv file',type=["csv"], accept_multiple_files = False)
df, dts, profile_groups =upload_csv_files(csv_files)

selected_dates=[]
selected_profiles=[]
with st.sidebar:
    if not dts: 
        st.info('#### No data to display')
    else:
        selected_dates = st.multiselect('Dates', dts, dts)
        selected_profiles = st.multiselect('Host Groups', profile_groups, profile_groups)

# if selcted_dates:
if dts:
    vul_per_host, plt_host_count, plt_vscore = format_df(df, selected_dates, selected_profiles)

    plot_kind = 'bar' if len(selected_dates) == 1 else 'line'
    # st.dataframe(vul_per_host)
    fig_1 = vul_per_host.plot(kind = plot_kind, title = 'Vulnerabilities Per Host', rot = 0, figsize=(10,6)).get_figure()
    st.pyplot(fig_1)
    fig_2 = plt_host_count.plot(kind = plot_kind, title = 'Host Count', rot = 0, figsize=(10,6)).get_figure()
    st.pyplot(fig_2)
    fig_3 = plt_vscore.plot(kind = plot_kind, title = 'Avg Vulnurability Score per Host', rot = 0, figsize=(10,6)).get_figure()
    st.pyplot(fig_3)
    
# st.download_button(label = 'Save to csv', data = convert_df(df), file_name = 'Log Summary Data.csv', mime = 'text/csv')
    



           