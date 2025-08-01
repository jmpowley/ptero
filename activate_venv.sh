VENV_DIR="/Users/Jonah/MISCADA/Project/masters_venv"
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

cd $VENV_DIR
source bin/activate
cd $SCRIPT_DIR