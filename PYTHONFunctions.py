from datetime import datetime, timedelta
import re, os
import psutil
from urllib.parse import urlencode
from platform import system as system_name
from subprocess import call as system_call
import RESTFunctions as RF
import clients as CL
import requests as req
import pathlib
import plotly
import plotly.graph_objects as go
from numpy import nanmean


# Edited from https://stackoverflow.com/questions/2953462/pinging-servers-in-python
def ping(host):
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """

    # Ping command count option as function of OS
    param = '-n' if system_name().lower() == 'windows' else '-c'

    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', param, '1', host]

    # Pinging
    return system_call(command) == 0


def exitOffice():
    ''' Kills Office processes

    :return:
    '''
    if system_name() == 'Windows':
        for proc in psutil.process_iter():
            if proc.name() == 'EXCEL.EXE' or proc.name() == 'WINWORD.EXE':
                psutil.Process(proc.pid).terminate()


def screenshots(starttime, endtime):
    screenshots = 'Screenshots'
    pathlib.Path(screenshots).mkdir(parents=True, exist_ok=True)

    screenshotsForDocx = 'Screenshots For Docx'
    pathlib.Path(screenshotsForDocx).mkdir(parents=True, exist_ok=True)

    outputdir = 'Stats Working Dir'
    pathlib.Path(outputdir).mkdir(parents=True, exist_ok=True)
    outputdir = 'Stats-' + formatedStart + "-" + formatedEnd
    pathlib.Path(outputdir).mkdir(parents=True, exist_ok=True)

    minutesFilterOut = 1

    createGraphs(CL.index, starttime, endtime,
                 RF.getBandwidthScale(CL.index, CL.Clients[CL.index]['OUTER_HOST'],
                                      CL.Clients[CL.index]['OUTER_SERVICE']))

    meanUP, meanDown, meanUnreachable, count = RF.getAllHostsAvailability(CL.index, starttime, endtime)
    print(meanUP, meanDown, count)
    createPieChart(["UP", "Unreachable", "Down"], ['#b2ff5f', '#f6ff00', '#ff2600'], [meanUP, meanDown],
                   name='Average Host Availlability')

    meanOK, meanWwarning, meanCritical, count = RF.getAllServicesAvailability(CL.index, starttime, endtime)
    print(meanOK, meanWwarning, meanCritical, count)
    createPieChart(["OK", "Warning", "Critical"], ['#b2ff5f', '#f6ff00', '#ff2600'],
                   [meanOK, meanWwarning, meanCritical], name='Average Service Availlability')

    RF.getAllHostsAvailability(CL.index, starttime, endtime)
    stateHistory = RF.getFullStateHistory(CL.index, starttime, endtime)
    RF.getAllHostsDowntimes(CL.index, starttime, endtime, 'Stats Working Dir', minutesFilterOut, stateHistory)
    RF.getAllInterfacesAvailability(CL.index, starttime, endtime, 'Stats Working Dir', minutesFilterOut, stateHistory)
    RF.getAllBandwidthAlerts(CL.index, starttime, endtime, 'Stats Working Dir', stateHistory)


def createGraphs(hostName, serviceName, starttime, endtime, scaleText):
    chunkSeconds = 86400
    step = 300

    time = []
    inbw = []
    outbw = []
    end = 0

    start = starttime
    end = starttime + chunkSeconds
    while start < endtime:

        body = {
            'apikey': CL.Clients[CL.index]['API_KEY'],
            'host_name': hostName,
            'service_description': serviceName,
            'start': start,
            'end': end,
            'step': step
        }
        qstr = urlencode(body)

        url = 'https://' + CL.Clients[CL.index]['HOST'] + '/nagiosxi/api/v1/objects/rrdexport/?' + qstr

        reChecks = 3
        backoff = 5
        for i in range(reChecks):
            try:
                response = req.request('GET', url, verify=False).json()
            except Exception as e:
                print(e)
            if not int(response["meta"]["rows"]) > 0:
                print("could Not retrieve chunk")
                time.sleep(backoff)
                backoff = i * 1.75 + backoff
            else:
                break

        for value in response['data']['row']:
            time.append(datetime.fromtimestamp(int(value['t'])))
            inbw.append(float("{0:.3f}".format(round(float(value['v'][0]), 3))))
            outbw.append(float("{0:.3f}".format(round(float(value['v'][1]), 3))))

        step = response['meta']['step']
        start += chunkSeconds
        end += chunkSeconds
        if end > endtime:
            end = endtime

    name = hostName + ' : ' + serviceName

    createOverlayGraph(time, inbw, outbw, name, scaleText)


def createOverlayGraph(time, inbw, outbw, name, scaleText):
    max_ = max(inbw + outbw)

    latest = str(max(time))
    max_in = max(inbw)
    max_in = format(max_in, '.2f')
    max_out = max(outbw)
    max_out = format(max_out, '.2f')

    mean_in = nanmean(inbw)
    mean_in = format(mean_in, '.2f')
    mean_out = nanmean(outbw)
    mean_out = format(mean_out, '.2f')

    fig = go.Figure(
        layout=dict(
            width=1750,
            height=360,
            title="<b>" + name + "</b>",

            paper_bgcolor='#FFFFFF',
            plot_bgcolor='#FFFFFF',
            legend=dict(orientation='v', yanchor='bottom', xanchor='center', y=-0.45, x=0.5),
            xaxis=dict(
                linecolor='#d5d5d5',
                linewidth=2,
                mirror=False
            ),
            yaxis=dict(
                title=scaleText,
                autorange=True,
                linecolor='#d5d5d5',
                linewidth=2,
                mirror=False
            )
        ))

    fig.add_trace(go.Scatter(
        mode='lines',
        x=time,
        y=inbw,
        name='incoming (Avg: ' + mean_in + ' ' + scaleText + ', Max: ' + max_in + ' ' + scaleText + ')',
        opacity=1,
        line=dict(
            color='#4089F9',
            width=1.2
        )
    ))

    fig.add_trace(go.Scatter(
        mode='lines',
        x=time,
        y=outbw,
        name='outgoing (Avg: ' + mean_out + ' ' + scaleText + ', Max: ' + max_out + ' ' + scaleText + ')',
        opacity=1,
        line=dict(
            color='#23B55E',
            width=1.2
        )
    ))

    fig.update_xaxes(showgrid=True, gridwidth=0.9, gridcolor='#c5c5c5', zeroline=True, tickmode="array")
    fig.update_yaxes(showgrid=True, gridwidth=0.7, gridcolor='#c5c5c5', zeroline=True, tickmode="array")

    now = datetime.now()
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    date_time = date_time.replace(":", "-")
    date_time = date_time.replace("/", "-")

    if not os.path.exists("Screenshots"):
        os.mkdir("Screenshots")
    fig.write_image("Screenshots/overlay_bwgraphs, " + date_time + ".png")

    if not os.path.exists("HTML"):
        os.mkdir("HTML")
    plotly.offline.plot(fig, filename='HTML/overlay_Bandwidth_Graph, ' + date_time + '.html')

    return fig


def createPieChart(labels, colors, values, name="pie"):
    title = "<b>" + name + "<b><br><br>"
    formatedValues = []
    for value in values:
        formatedValues.append(format(value, '.2f'))

    fig = go.Figure(data=[go.Pie(labels=labels,
                                 values=formatedValues)])

    fig.update_traces(hoverinfo='percent', textinfo='percent', textfont_size=20,
                      marker=dict(colors=colors, line=dict(color='#000000', width=2)))

    fig.update(layout_title_text=title)

    now = datetime.now()
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    date_time = date_time.replace(":", "-")
    date_time = date_time.replace("/", "-")

    if not os.path.exists("Screenshots"):
        os.mkdir("Screenshots")
    fig.write_image("Screenshots/" + name + "-" + date_time + ".png")

    if not os.path.exists("HTML"):
        os.mkdir("HTML")

    plotly.offline.plot(fig, filename='HTML/' + name + '-' + date_time + '.html')

def convert_month_to_str(int):
    if(int==1):
        return 'Jan'
    if (int == 2):
        return 'Feb'
    if (int == 3) :
        return 'Mar'
    if (int == 4):
        return 'Apr'
    if (int == 5):
        return 'May'
    if (int == 6):
        return 'Jun'
    if (int == 7):
        return 'Jul'
    if (int == 8):
        return 'Aug'
    if (int == 9):
        return 'Sep'
    if (int == 10):
        return 'Oct'
    if (int == 11):
        return 'Nov'
    if (int == 12):
        return 'Dec'

def convert_month_to_int(str):
    if(str=='Jan'):
        return 1
    if (str == 'Feb'):
        return 2
    if (str == 'Mar') :
        return 3
    if (str == 'Apr'):
        return 4
    if (str == 'May'):
        return 5
    if (str == 'Jun'):
        return 6
    if (str == 'Jul'):
        return 7
    if (str == 'Aug'):
        return 8
    if (str == 'Sep'):
        return 9
    if (str == 'Oct'):
        return 10
    if (str == 'Nov'):
        return 11
    if (str == 'Dec'):
        return 12

