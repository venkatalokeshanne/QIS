// Shifts a [start, end] date range (YYYY-MM-DD strings) back or
// forward by its own span, so consecutive clicks step through
// adjacent, non-overlapping periods of the same length -- "previous
// month" if the currently selected range happens to span a month,
// "previous day" if it's a single day, etc -- without needing to
// special-case calendar units.

// Parses a YYYY-MM-DD string as a LOCAL calendar date (midnight local
// time), not a UTC instant -- Date's own ISO-string parsing treats a
// date-only string as UTC midnight, which can silently land on the
// wrong day once converted back to local time for display/comparison.
function parseLocalDate(value) {
  const [year, month, day] = value.split('-').map(Number)
  return new Date(year, month - 1, day)
}

function toDateInputValue(date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

// direction: -1 for the previous period, 1 for the next.
export function shiftDateRange(startDate, endDate, direction) {
  const start = parseLocalDate(startDate)
  const end = parseLocalDate(endDate)
  const spanDays = Math.round((end - start) / 86_400_000)
  const shiftDays = (spanDays + 1) * direction

  const newStart = new Date(start)
  newStart.setDate(newStart.getDate() + shiftDays)
  const newEnd = new Date(end)
  newEnd.setDate(newEnd.getDate() + shiftDays)

  return { startDate: toDateInputValue(newStart), endDate: toDateInputValue(newEnd) }
}
