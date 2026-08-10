function SubClaimCard({ subClaim }: { subClaim: any }) {
  return (
    <div className="sub-claim">
      <h3>{subClaim.text}</h3>
      <p className={`strength strength-${subClaim.strength.replaceAll(' ', '-')}`}>
        {subClaim.strength}
        {subClaim.reused && <span className="reused-badge"> (reused from earlier research)</span>}
      </p>
      <ul className="evidence-list">
        {subClaim.evidence.map((e: any, j: number) => (
          <li key={j} className={`evidence evidence-${e.relation}`}>
            <strong>{e.relation}</strong>: {e.summary}{' '}
            <a href={e.url} target="_blank" rel="noreferrer">
              source
            </a>{' '}
            <span className="credibility" title="Credibility score">
              {Math.round(e.credibility_score * 100)}%
            </span>
          </li>
        ))}
      </ul>
    </div>
  )
}

export default SubClaimCard
