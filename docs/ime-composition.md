# IME-safe Enter shortcuts

Custom Enter-to-send or Enter-to-search handlers must distinguish an IME
confirmation from a submission. Korean, Japanese and Chinese input methods can
use Enter while composing text; sending at that point can publish unfinished text.
This guidance covers web keyboard handlers, not a new native input implementation.

## Plain DOM example

Use this shortcut on a labelled textarea with a separate submit button. Leave
Shift+Enter available for newlines. This example handles only unmodified Enter;
Ctrl, Meta and Alt shortcuts remain the application's separate policy. Route submission through the form so native
validation and the submit handler still run.

```html
<form id="message-form">
  <label for="message">Message</label>
  <textarea id="message" name="message" required></textarea>
  <button type="submit">Send</button>
</form>
```

```js
const textarea = document.querySelector('#message');
const form = document.querySelector('#message-form');

textarea.addEventListener('keydown', e => {
  if (e.key !== 'Enter' || e.shiftKey || e.ctrlKey || e.metaKey || e.altKey) return;
  // Suppress newline/implicit submit before deciding whether to send.
  e.preventDefault();
  if (e.isComposing || e.keyCode === 229) return;
  if (!e.repeat) form.requestSubmit();
});
```

`isComposing` is the primary check. The deprecated `keyCode === 229` check is a
narrow compatibility fallback for IME-handled keys on affected browsers, including
Safari configurations that deliver the confirming keydown after compositionend.
It is not a replacement for `event.key` or a general keyboard API recommendation.
A WebKit event-ordering fix was subsequently reverted (see issues 311717 and
317127). Do not assume the issue is confined to older Safari releases or remove
the fallback based only on the resolved status of issue 165004. Verify the exact
released browser/OS/input-method combinations you support.

The handled Enter path cancels its default action before checking composition,
following Chrome's guidance, so returning from the 229 path does not leave a
newline or implicit form submission behind. Actual IME confirmation behavior
still needs the manual checks below.

In React, read `isComposing` from `event.nativeEvent` in an
`onKeyDown` handler. A compositionstart/compositionend flag alone does not cover
the Safari ordering described above. Do not submit from compositionend:
finishing text composition is not consent to send it.

The `keyCode` fallback can also be read from that native event; React also exposes
keyCode on its keyboard event. This guide's executable example is plain DOM,
not a mounted React component.

Virtual keyboards can report `Unidentified` or `Process` rather than `Enter`.
Do not interpret every 229 event as a submit request. Keep the explicit Send button
available so mobile users can submit without a hardware keyboard shortcut.

An ordinary single-line input inside a form, with no custom Enter handler, should
keep native form submission. Do not add this handler to every input. For a custom
single-line search shortcut, adapt the newline policy and apply the same IME guard.

This example requires `HTMLFormElement.requestSubmit()` support. If your target
browser lacks it, retain native form submission or use a separately tested submit
button path; do not assume this example supports every legacy Safari version.

## Verification

Automated sample checks execute both the CSV and this document's JavaScript
example. They cover handler branches, not an operating system IME.
Before claiming browser/IME compatibility, manually check the supported browser,
OS and input-method combinations and record their versions:

1. Compose Korean text such as `한글` and press Enter while composition is active.
   The composition-confirming key must not send, search or clear the field.
2. After composition has ended, press a separate Enter. Submit once; holding it
   must not cause repeated submissions. Check the intended modifier-key policy.
3. Check Japanese conversion and Chinese candidate confirmation independently;
   Korean-only testing does not establish support for every CJK input method.
4. Keep Shift+Enter newlines, normal typing, paste and the explicit Send button
   usable. Confirm that an empty required field still fails native validation.
5. On affected Safari versions, inspect an IME-confirming keydown with
   isComposing false and keyCode 229; it must not activate the custom shortcut.
6. On supported mobile keyboards, confirm that the visible Send button works
   even when the keyboard does not emit an identifiable Enter keydown.

## References

- [W3C UI Events: key events during composition](https://www.w3.org/TR/uievents/#events-composition-key-events)
- [Chrome for Developers: IME-safe enter-to-submit](https://developer.chrome.com/docs/modern-web-guidance/guides/forms/ime-safe-enter-submit)
- [WebKit issue 165004: original event-ordering report](https://bugs.webkit.org/show_bug.cgi?id=165004)
- [WebKit issue 311717: fix and later reversion discussion](https://bugs.webkit.org/show_bug.cgi?id=311717)
- [WebKit issue 317127: disabling the changed event ordering](https://bugs.webkit.org/show_bug.cgi?id=317127)
