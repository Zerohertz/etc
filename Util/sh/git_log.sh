START_DATE="2025-03-04"

git --no-pager log --since="$START_DATE" --format='%H %aI' | while read -r hash date_iso; do
	day_of_week=$(gdate -d "$date_iso" '+%u' 2>/dev/null || date -d "$date_iso" '+%u' 2>/dev/null)
	hour=$(gdate -d "$date_iso" '+%H' 2>/dev/null || date -d "$date_iso" '+%H' 2>/dev/null)
	if [[ -n "$day_of_week" && -n "$hour" ]]; then
		if [[ "$day_of_week" -ge 1 && "$day_of_week" -le 5 ]]; then
			if [[ "$hour" -ge 9 && "$hour" -lt 18 ]]; then
				git --no-pager show -s --format='commit %H%nAuthor: %an <%ae>%nDate:   %ad%n%n%w(0,4,4)%s%n%n%b' "$hash"
				echo "----------------------------------------"
			fi
		fi
	fi
done
