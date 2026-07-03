export default function Card({ tight, className = '', children, ...props }) {
  const classes = ['card', tight ? 'card-tight' : '', className].filter(Boolean).join(' ')
  return (
    <div className={classes} {...props}>
      {children}
    </div>
  )
}
