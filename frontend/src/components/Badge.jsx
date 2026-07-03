export default function Badge({ accent, children }) {
  return <span className={`badge${accent ? ' badge-accent' : ''}`}>{children}</span>
}
