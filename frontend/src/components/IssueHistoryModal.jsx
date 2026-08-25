import Modal from './Modal'
import IssueCard from './IssueCard'
import { EmptyHint } from './ui'

export default function IssueHistoryModal({ open, onClose, issues = [], title = 'Report History', subtitle, actions }) {
  return (
    <Modal open={open} onClose={onClose} title={title} subtitle={subtitle} maxWidth={460}>
      <div className="issue-list history-list">
        {issues.length === 0 ? (
          <EmptyHint>Nothing reported yet</EmptyHint>
        ) : (
          issues.map((i) => <IssueCard key={i.id} issue={i} actions={actions} />)
        )}
      </div>
    </Modal>
  )
}
