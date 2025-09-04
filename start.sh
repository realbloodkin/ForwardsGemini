#echo "Cloning Repo...."
#if [ -z $BRANCH ]
#then
 # echo "Cloning main branch...."
 # git clone https://github.com/Mr-Syd/FR Mr-Syd/FR
#else
#  echo "Cloning $BRANCH branch...."
 # git clone https://github.com/Mr-Syd/FR -b $BRANCH /main
#fi
#cd Mr-SyD-OrG/Forw
pip3 install -U -r requirements.txt
echo "Starting Bot...."
python3 main.py
