python get_latebreaking_data.py

sed -i -e 's/<u>/\\underline\{/g' 2021_abstracts.csv
sed -i -e 's/<\/u>/\}/g' 2021_abstracts.csv
sed -i -e 's/<sup>/\\textsuperscript\{/g' 2021_abstracts.csv
sed -i -e 's/<\/sup>/\}/g' 2021_abstracts.csv
sed -i -e 's/\ \&\ /\ \\\&\ /g' 2021_abstracts.csv
sed -i -e 's/\&E/\\\&E/g' 2021_abstracts.csv
sed -i -e 's/A\&/A\\\&/g' 2021_abstracts.csv
sed -i -e 's/\_/\\\_/g' 2021_abstracts.csv
sed -i -e 's/\\n\\n/\\linebreak/g' 2021_abstracts.csv

# remove first line
for FILE in 2021_authors_index.csv 2021_categories_index.csv ; do
tail -n +2 "$FILE" > "$FILE.tmp" && mv "$FILE.tmp" "$FILE"
done

lualatex -interaction=nonstopmode ohbm2021_abstract_book.tex
lualatex -interaction=nonstopmode ohbm2021_abstract_book.tex
