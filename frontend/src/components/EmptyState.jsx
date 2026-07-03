export default function EmptyState({ title, body, action }) {
  return (
    <div className="empty-state">
      <div className="empty-state-title">{title}</div>
      {body && <p className="empty-state-body">{body}</p>}
      {action}
    </div>
  )
}
