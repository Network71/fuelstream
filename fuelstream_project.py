import fastf1
from matplotlib import pyplot as plt
from fastf1 import plotting
import numpy as np
import pandas as pd
from timple.timedelta import strftimedelta
from fastf1.core import Laps

def main_menu():
    print("Welcome to fuelstream.")
    print()
    print("1: Compare fastest laps of two drivers")
    print("2: Position changes throughout a race")
    print("3: View map of track")
    print("4: Qualifying results")

    user_choice = int(input("> "))

    if user_choice == 1:
        drivers_pace()
    elif user_choice == 2:
        position_changes()
    elif user_choice == 3:
        track_map()
    elif user_choice == 4:
        quali_results()

def drivers_pace():
    print("Format: (Year) (Track) (Session) (Driver1) (Driver2)")
    user_input = input("Enter session details: ")
    session_details = user_input.split(" ")
    session_details[0] = int(session_details[0])

    #get session data
    fastf1.plotting.setup_mpl(mpl_timedelta_support=True, color_scheme="fastf1")
    session = fastf1.get_session(session_details[0], session_details[1], session_details[2])
    session.load()

    #get driver laps
    driver1_lap = session.laps.pick_drivers(session_details[3]).pick_fastest()
    driver2_lap = session.laps.pick_drivers(session_details[4]).pick_fastest()

    #get lap telemtry
    driver1_telemtry = driver1_lap.get_car_data().add_distance()
    driver2_telemtry = driver2_lap.get_car_data().add_distance()

    #plotting
    team1_color = fastf1.plotting.get_team_color(driver1_lap['Team'], session=session)
    team2_color = fastf1.plotting.get_team_color(driver2_lap['Team'], session=session)

    fig, ax = plt.subplots()
    ax.plot(driver1_telemtry['Distance'], driver1_telemtry['Speed'], color=team1_color, label=session_details[3])
    ax.plot(driver2_telemtry['Distance'], driver2_telemtry['Speed'], color=team2_color, label=session_details[4])

    ax.set_xlabel("Distance in m")
    ax.set_ylabel("Speed in km/h")

    ax.legend()
    plt.suptitle("Fastest lap comparison")
    plt.show()

def position_changes():

    #session details
    print("Format: (Year) (Track)")
    user_input = input("Enter session details: ")
    session_details = user_input.split(" ")
    session_details[0] = int(session_details[0])

    #set up plot
    fastf1.plotting.setup_mpl(mpl_timedelta_support=False, color_scheme='fastf1')

    #load session
    session = fastf1.get_session(session_details[0], session_details[1], 'R')
    session.load(telemetry=False, weather=False)
    fig, ax = plt.subplots(figsize=(8.0, 4.9))

    #plotting
    for drv in session.drivers:
        drv_laps = session.laps.pick_drivers(drv)
        if drv_laps.empty:
            continue
        abb = drv_laps['Driver'].iloc[0]
        style = fastf1.plotting.get_driver_style(identifier=abb, style=['color', 'linestyle'], session=session)
        ax.plot(drv_laps['LapNumber'], drv_laps['Position'], label=abb, **style)
        
    ax.set_ylim([20.5, 0.5])
    ax.set_yticks([1,5,10,15,20])
    ax.set_xlabel(['Lap'])
    ax.set_ylabel(['Position'])

    ax.legend(bbox_to_anchor=(1.0,1.02))
    plt.tight_layout()

    plt.show()

def track_map():
    track_name = input("Enter track name: ")

    #loading all session data
    session = fastf1.get_session(2021, track_name, 'Q')
    session.load()

    lap = session.laps.pick_fastest()
    pos = lap.get_pos_data()
    circuit_info = session.get_circuit_info()

    #helper function for rotating points around origin of the coordinate system
    def rotate(xy, *, angle):
        rot_mat = np.array([[np.cos(angle), np.sin(angle)],
                            [-np.sin(angle), np.cos(angle)]])
        return np.matmul(xy, rot_mat)

    #get coordinates of track map from telemtry and rotate the coors so map is oriented correctly
    track = pos.loc[:, ('X', 'Y')].to_numpy()
    track_angle = circuit_info.rotation / 180 * np.pi 
    rotated_track = rotate(track, angle=track_angle)
    plt.plot(rotated_track[:, 0], rotated_track[:, 1])

    #plot corner markets
    offset_vector = [500, 0]
    for _, corner in circuit_info.corners.iterrows():
        txt = f"{corner['Number']}{corner['Letter']}"
        offset_angle = corner['Angle'] / 18 * np.pi
        offset_x, offset_y = rotate(offset_vector, angle = track_angle)
        text_x = corner['X'] + offset_x
        text_y = corner['Y'] + offset_y
        text_x, text_y = rotate([text_x, text_y], angle=track_angle)
        track_x, track_y = rotate([corner['X'], corner['Y']], angle=track_angle)

        plt.scatter(text_x, text_y, color='grey', s=140)
        plt.plot([track_x, text_x], [track_y, text_y], color='grey')
        plt.text(text_x, text_y, txt, va='center_baseline', ha='center', size='small', color='white')

    #plotting
    plt.title(session.event['Location'])
    plt.xticks([])
    plt.yticks([])
    plt.axis('equal')
    plt.show()

def quali_results():

    fastf1.plotting.setup_mpl(mpl_timedelta_support=True, color_scheme=None)

    #session details
    print("Format: (Year) (Track)")
    user_input = input("Enter session details: ")
    session_details = user_input.split(" ")
    session_details[0] = int(session_details[0])

    session = fastf1.get_session(session_details[0], session_details[1], 'Q')
    session.load()

    #driver array
    drivers = pd.unique(session.laps['Driver'])

    #get fastest lap and create object, sort and reindex
    list_fastest_laps = list()
    for drv in drivers:
        drvs_fastest_lap = session.laps.pick_drivers(drv).pick_drivers(drv).pick_fastest()
        list_fastest_laps.append(drvs_fastest_lap)
    fastest_laps = Laps(list_fastest_laps).sort_values(by='LapTime').reset_index(drop=True)

    pole_lap = fastest_laps.pick_fastest()
    fastest_laps['LapTimeDelta'] = fastest_laps['LapTime'] - pole_lap['LapTime']

    #team color list
    team_colors = list()
    for index, lap in fastest_laps.iterlaps():
        color = fastf1.plotting.get_team_color(lap['Team'], session=session)
        team_colors.append(color)

    #plotting
    fig, ax = plt.subplots()
    ax.barh(fastest_laps.index, fastest_laps['LapTimeDelta'], color = team_colors, edgecolor='grey')
    ax.set_yticks(fastest_laps.index)
    ax.set_yticklabels(fastest_laps['Driver'])

    ax.invert_yaxis()

    ax.set_axisbelow(True)
    ax.xaxis.grid(True, which='major', linestyle='--', color='black', zorder=-1000)

    lap_time_string = strftimedelta(pole_lap['LapTime'], '%m:%s.%ms')
    plt.suptitle(f"{session.event['EventName']} {session.event.year} Qualifying\n" f"Fastest Lap: {lap_time_string} ({pole_lap['Driver']})")
    plt.show()

main_menu()
