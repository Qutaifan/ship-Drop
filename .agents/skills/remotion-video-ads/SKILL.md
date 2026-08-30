---
name: remotion-video-ads
description: Build and render high-converting, programmatic 9:16 vertical video ads for TikTok, Instagram Reels, and YouTube Shorts using React and Remotion with zero marginal rendering cost.
---

# Remotion Programmatic Video Ads Skill

This skill teaches agents how to construct, parameterize, and render conversion-optimized 9:16 vertical video ads using React and **Remotion**.

---

## 1. Composition Architecture

All vertical video ads follow a 1080x1920 (9:16) format rendered at 30 FPS, structured into three distinct temporal acts:

```
0s ────── 3s ────────────────── 12s ───────────────── 15s (450 frames @ 30fps)
┌────────────┬────────────────────────┬─────────────┐
│  Act 1:    │  Act 2:                │  Act 3:     │
│  The Hook  │  The Transformation /  │  The Offer  │
│  (Stop)    │  Demonstration         │  & CTA      │
└────────────┴────────────────────────┴─────────────┘
```

---

## 2. Core Remotion Component Structure

```tsx
import { AbsoluteFill, Sequence, useCurrentFrame, useVideoConfig, interpolate, spring } from 'remotion';

export interface AdProps {
  hookHeadline: string;
  subheadline: string;
  productImage: string;
  ctaText: string;
  accentColor: string;
}

export const VerticalVideoAd: React.FC<AdProps> = ({
  hookHeadline,
  subheadline,
  productImage,
  ctaText,
  accentColor = '#FF4D4D',
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Entrance spring animation for hook text
  const textEntrance = spring({
    frame,
    fps,
    config: { damping: 12, mass: 0.5 },
  });

  return (
    <AbsoluteFill style={{ backgroundColor: '#F8F9FA', fontFamily: 'Inter, sans-serif' }}>
      {/* Act 1: Hook (Frames 0 - 90 / 0-3s) */}
      <Sequence from={0} durationInFrames={90}>
        <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', padding: 40 }}>
          <h1
            style={{
              fontSize: 64,
              fontWeight: 800,
              textAlign: 'center',
              color: '#111827',
              transform: `scale(${textEntrance})`,
              lineHeight: 1.15,
            }}
          >
            {hookHeadline}
          </h1>
          <p style={{ fontSize: 32, color: '#6B7280', marginTop: 20 }}>{subheadline}</p>
        </AbsoluteFill>
      </Sequence>

      {/* Act 2: Demonstration / Staging (Frames 90 - 360 / 3-12s) */}
      <Sequence from={90} durationInFrames={270}>
        <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center' }}>
          <img
            src={productImage}
            alt="Product"
            style={{
              width: '80%',
              borderRadius: 24,
              boxShadow: '0 20px 40px rgba(0,0,0,0.15)',
            }}
          />
        </AbsoluteFill>
      </Sequence>

      {/* Act 3: Call To Action (Frames 360 - 450 / 12-15s) */}
      <Sequence from={360} durationInFrames={90}>
        <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', backgroundColor: '#111827' }}>
          <h2 style={{ fontSize: 52, color: '#FFFFFF', fontWeight: 800, textAlign: 'center' }}>
            {ctaText}
          </h2>
          <div
            style={{
              marginTop: 30,
              padding: '16px 36px',
              backgroundColor: accentColor,
              borderRadius: 100,
              color: '#FFFFFF',
              fontSize: 28,
              fontWeight: 700,
            }}
          >
            Tap Below to Order
          </div>
        </AbsoluteFill>
      </Sequence>
    </AbsoluteFill>
  );
};
```

---

## 3. Best Practices for Direct-Response Ads

1. **Sub-3s Visual Stop**: Text scale spring + high-contrast typography must trigger within the first 15 frames ($0.5$s).
2. **Audio Sync**: Align Sequence cuts (`from` frame numbers) with beat markers from a 120–128 BPM backing track.
3. **Parameterization**: Pass product props (price, title, image assets) via JSON files so batch rendering can output 10+ hook variations from the command line:
   ```bash
   npx remotion render src/index.ts ShortFormAd out/hook1.mp4 --props='{"hookHeadline":"Tired of messy cables?"}'
   ```
4. **Local Hardware Rendering**: Remotion leverages headless Chromium with hardware acceleration; render on local RTX 4060 with `--concurrency=4` for rapid compilation at €0 marginal cost.
