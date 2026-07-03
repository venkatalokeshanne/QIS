export default function Button({ variant = 'secondary', size, className = '', ...props }) {
  const classes = ['btn', `btn-${variant}`, size === 'sm' ? 'btn-sm' : '', className]
    .filter(Boolean)
    .join(' ')
  return <button className={classes} {...props} />
}
