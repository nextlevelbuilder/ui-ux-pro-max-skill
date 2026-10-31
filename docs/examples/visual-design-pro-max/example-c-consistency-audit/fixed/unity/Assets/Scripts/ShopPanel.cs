// FIXTURE: C# with intentional drift (see expected-findings.md). Not compilable on purpose.
using UnityEngine;
using UnityEngine.UIElements;
using DG.Tweening;

public class ShopPanel : MonoBehaviour
{
    // color.near-duplicate: 0.98f,0.5f,0.31f -> #FA804F, accent is #FF8A4C
    static readonly Color Highlight = new Color(0.98f, 0.5f, 0.31f);
    // in palette (primary #3B5BDB) -> no finding
    static readonly Color32 Primary = new Color32(59, 91, 219, 255);

    void Show(VisualElement root)
    {
        Color pink;
        if (ColorUtility.TryParseHtmlString("#E91E63", out pink)) // color.off-palette #E91E63
        {
            root.style.backgroundColor = pink;
        }
        root.transform.DOScale(1.1f, 0.337f);      // duration.off-scale 337ms (DOTween, seconds)
        root.DOFade(1f, 0.2f);                     // 200ms -> in scale, no finding
        DOTween.To(() => 0f, v => { }, 1f, 0.35f); // 350ms -> in scale, no finding
    }
}
