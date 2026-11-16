interface StyleCardTitleProps {
  name: string;
  onOpen?: () => void;
}

const TITLE_CLASS =
  "text-sm font-semibold text-gray-900 dark:text-gray-100 leading-tight";

// The title is a real button so keyboard and screen reader users can open the
// detail modal; making the whole card a button would nest its other controls.
// The focus mark is an outline, not a ring: forced-colors mode drops the
// box-shadow a ring is drawn with.
export function StyleCardTitle({ name, onOpen }: StyleCardTitleProps) {
  if (!onOpen) return <h3 className={TITLE_CLASS}>{name}</h3>;

  return (
    <h3 className={TITLE_CLASS}>
      <button
        type="button"
        aria-haspopup="dialog"
        onClick={onOpen}
        className="text-left rounded focus:outline-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-500"
      >
        {name}
      </button>
    </h3>
  );
}
