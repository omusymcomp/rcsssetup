#!/bin/bash

#第1引数 試合数

#チームをリストで渡す
Team="${HOME}/rcss/team/*"	#*を付けると中にあるファイル全部持ってきてくれる
#echo ${Team} #全teamの場所のリストが作成できていることを確認

#日付のファイルを指定場所に作る
DATE=`date +%Y%m%d%0k%M`
mkdir ${HOME}/rcss/log_analysis/log/${DATE}

#echo ${Team[@]}
#echo ${Team[0]}	#Team[0]にすべて入っていたので、これを分割する

#スペースで分割してTeam_Listに入れる
Team_List=(${Team/ /})
#確認用
#echo ${Team_List[2]}
#echo ${Team_List[1]}
#echo ${Team_List[0]}
#echo ${#Team_List[@]}	#チーム数はこれで確認できる

#for filepath in ${Team}; do
#	if [ -d ${filepath} ] ; then
#		Team_List+=("${filepath}")
#	fi
#done



#seq ${#Team_List[@]}	#seqはこんな感じで動く
#リストのforループの動かし方
#echo "ディレクトリ一覧"
#for ((i=0; i<${#Team_List[@]}; i++)) do
#	echo ${i}
#	echo "${Team_List[${i}]}"
#done



LOGDIR="${HOME}/rcss/log_analysis/log/${DATE}"
#cd "./team/aaCyrus2018_new/"
#cd "./team/Fraunited2018_new/"
# game loop
for ((i=0; i<1; i++)) do
	for ((j=i+1; j<2; j++)) do
		#echo $i + $j
		#echo ${Team_List[i]} + ${Team_List[j]}
		#echo $count
		if [ $i = $j ]; then
			#echo "同一チームなのでパス"
			continue
	    fi
	  	#Git管理している方のHELIOSのパス
		Team_L="'${HOME}/rcss/HELIOS/helios/src/start-ocl.sh'"
		#Team_L="${Team_List[i]}/startAll"
		#Team_L="'${Team_List[i]}/src/start-ocl.sh'"
		#Team_R="${Team_List[j]}/src/start.sh"
		Team_R="${Team_List[j]}/start.sh"
		#Team_R="'${Team_List[j]}/src/start.sh -t testAG'" #同名チームでの試合
		echo "$Team_R"
		echo "$Team_R"
		echo "$Team_L"
		count=1
		#$1は試合数で実行時に引数として記入する
		while [ $count -le $1 ] ; do	#-leは<=の意味
			echo "--------------------"
			echo " ${Team_List[i]} vs ${Team_List[j]}"
			echo " Game ${count}"
			echo "--------------------"
			count=$(($count+1))

			DATE=`date +%Y%m%d%0k%M`
			mode=true
			#echo "チームL" + ${Team_L}
			#echo "チームR" + ${Team_R}
			if [ ${Team_L} = "${HOME}/rcss/log_analysis/team/fractals/startAll" ] || [ ${Team_L} = "${HOME}/rcss/log_analysis/team/fraunited/startAll" ]; then
				#echo ${Team_L} + ${Team_R}
				mode=false
				#echo "Team_Lがsynch対応外です。modeをfalseに切り替えました"
			fi
			if [ ${Team_R} = "${HOME}/rcss/log_analysis/team/fractals/startAll" ] || [ ${Team_R} = "${HOME}/rcss/log_analysis/team/fraunited/startAll" ]; then
				#echo ${Team_L} + ${Team_R}
				mode=false
				#echo "Team_Rがsynch対応外です。modeをfalseに切り替えました"
			fi
			#echo "mode" + ${mode}
			
			#../../bin/rcssserver server::auto_mode = 1 \
			#./bin/rcssserver server::auto_mode = 1 \
			 #server::fixed_teamname_l = 'AG2D' \
       				   #server::fixed_teamname_r = 'testAG2D' \
			l_name="AG2D"
			r_name="testAG2D"
			$HOME/local/bin/rcssserver server::auto_mode = 1 \
					   server::fixed_teamname_l = 'HELIOS2019' \
					   server::synch_mode = ${mode} \
					   server::team_l_start = ${Team_L} server::team_r_start = ${Team_R} \
					   server::kick_off_wait = 50 \
					   server::half_time = 300 \
					   server::nr_normal_halfs = 2 server::nr_extra_halfs = 0 \
					   server::penalty_shoot_outs = 0 \
					   server::game_logging = 1 server::text_logging = 1 \
					   server::game_log_dir = "${LOGDIR}" server::text_log_dir = "${LOGDIR}" \
					   2>&1 | tee ${LOGDIR}/${DATE}.log
			sleep 0.1
		done
	done
done
