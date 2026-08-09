function SubClaimCard({ subClaim }: { subClaim: any }) {
  return (
    <div className="sub-claim">
      <h3>{subClaim.text}</h3>
      <p className={`strength strength-${subClaim.strength.replaceAll(' ', '-')}`}>
        {subClaim.strength}
      </p>
      <ul className="evidence-list">
        {subClaim.evidence.map((e: any, j: number) => (
          <li key={j} className={`evidence evidence-${e.relation}`}>
            <strong>{e.relation}</strong>: {e.summary}{' '}
            <a href={e.url} target="_blank" rel="noreferrer">
              source
            </a>
          </li>
        ))}
      </ul>
    </div>
  )
}

export default SubClaimCard
