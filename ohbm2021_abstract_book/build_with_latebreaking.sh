python get_latebreaking_data.py

sed -i -e 's/<u>/\\underline\{/g' latebreaking_abstract.csv
sed -i -e 's/<\/u>/\}/g' latebreaking_abstract.csv
sed -i -e 's/<sup>/\\textsuperscript\{/g' latebreaking_abstract.csv
sed -i -e 's/<\/sup>/\}/g' latebreaking_abstract.csv
sed -i -e 's/\ \&\ /\ \\\&\ /g' latebreaking_abstract.csv
sed -i -e 's/\&E/\\\&E/g' latebreaking_abstract.csv
sed -i -e 's/A\&/A\\\&/g' latebreaking_abstract.csv
sed -i -e 's/\_/\\\_/g' latebreaking_abstract.csv
sed -i -e 's/\\n\\n/\\linebreak/g' latebreaking_abstract.csv

# remove first lene
for FILE in latebreaking_authors_index.csv latebreaking_categories_index.csv; do
tail -n +2 "$FILE" > "$FILE.tmp" && mv "$FILE.tmp" "$FILE"
done
