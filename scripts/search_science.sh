#! /bin/bash
source $HOME/.bashrc_conda

# Crawl script

# Get crawl name
if [ "$1" != "" ]; then
    # Supplied as argument
    Crawl="$1"
else
    # Or use today's date
    Today=$(date +"%Y%m%d")
    Crawl="/net/data/nir-data/scisearch/initial_collection/$Today"
    mkdir -p "$Crawl"
fi

# Enter project directory
cd /home/nir/repos/WebSearcher

Queries="queries_test_20220815.csv"
cp "$Queries" "$Crawl"

# Crawl args
args=(
    -i "$Queries"
    -o "$Crawl" 
)

# Activate virtual environment
conda activate py310
# source ~/.virtualenvs/audits/bin/activate

# Print environment and conlsdfig details
echo "PATH:" $PATH    # current path
echo "PWD: " $PWD     # current directory
echo "Crawl: $Crawl"  # crawl directory
echo $(python --version) # current python

# Collect SERPs
# Output: $Crawl/{serps.json.bz2, results.json}
python scripts/multi_search.py "${args[@]}"

# sync results to dropbox
/home/nir/bin/dropbox_uploader.sh -s -p upload "$Crawl" /SciSearches
