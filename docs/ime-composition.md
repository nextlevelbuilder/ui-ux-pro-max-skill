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
  // Let the IME handle confirmation; do not send or clear the text.
  if (e.isComposing || e.keyCode === 229) return;
  e.preventDefault();
  if (!e.repeat) form.requestSubmit();
});
```

`isComposing` is the primary check. The deprecated `keyCode === 229` check is a
narrow compatibility fallback for IME-handled keys on affected browsers, notably
older Safari versions that deliver the confirming keydown after compositionend.
It is not a replacement for `event.key` or a general keyboard API recommendation.
Do not infer that all current Safari versions have that event-ordering issue.

In React, read `isComposing` from `event.nativeEvent` in an
`onKeyDown` handler. A compositionstart/compositionend flag alone does not cover
the older Safari ordering described above. Do not submit from compositionend:
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
- [WebKit issue 165004: historical event ordering and resolution](https://bugs.webkit.org/show_bug.cgi?id=165004)
