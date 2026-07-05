import Habit_tracker_groundwork as gw


option=gw.option_menu()

if option=="Add a new habit to track":
    gw.new_habit()
elif option=="Log completion of a habit":
    gw.completion()
elif option=="View habit streaks and statistics":
    gw.stats()
elif option=="Edit or remove habits":
    gw.modify()
else:
    gw.All()