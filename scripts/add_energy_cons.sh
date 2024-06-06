for seed in "0" "1" "2" "3" "4" "5" "6" "7" "8" "9";
do
  # Scenario 1
  #for algo in "GTSP";#"MILP" "DSA" "GTSP";
  #do
    # vardrones
  #  for nu in "1" "2" "3" "4" "5";
  #  do
  #    for nd in "10";
  #    do
  #      python3 -m src.extract_battery_consumption -nu ${nu} -nd ${nd} -filename scenario_P2_50_${seed}.json -algorithm ${algo}
  #    done;
  #  done;
    # vardeliveries
  #  for nu in "3";
  #  do
  #    for nd in "3" "6" "9" "12";
  #    do
  #      python3 -m src.extract_battery_consumption -nu ${nu} -nd ${nd} -filename scenario_P2_50_${seed}.json -algorithm ${algo}
  #    done;
  #  done;
  #done;
  # Scenario 2
  for algo in "GTSP" "DSA" "RR" "RND";
  do
    # vardrones
    #for nu in "20" "25" "30" "35" "40" "45" "50";#
    #do
    #  for nd in "100";
    #  do
    #    python3 -m src.extract_battery_consumption -nu ${nu} -nd ${nd} -filename scenario_P2_50_${seed}.json -algorithm ${algo}
    #  done;
    #done;
    # vardeliveries
    for nu in "50";
    do
      for nd in "100" "150" "200" "250" "300" "350" "400" "450" ;
      do
        python3 -m src.extract_battery_consumption -nu ${nu} -nd ${nd} -filename scenario_P2_50_${seed}.json -algorithm ${algo}
      done;
    done;
  done;
done;
wait;



