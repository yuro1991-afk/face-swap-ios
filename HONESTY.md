# Honesty

```
false_green: 0
```

## Located

The fully working **local** face swap on this host is **MultoModa Face Studio**:

- Path: `G:\AI-Home\projects\multomoda-face-studio`
- Health: `http://127.0.0.1:8855/api/health` → `status: ok`, `local_only: true`, engines ready
- Models: `G:\AI-Home\models\insightface\inswapper_128.onnx` + `buffalo_l`
- Bind: **127.0.0.1 only** — an iPhone cannot reach it without this gateway

`:3000` is a *different* app (Remix MVLLM, `provider: spacexai`). That is not the local engine.

## iOS install — what is true

1. You **cannot** download this git repo onto an iPhone and get a native App Store app. Apple requires a signed IPA.
2. This Windows PC **cannot** compile Xcode / produce an IPA.
3. What **does** work on any iPhone: Safari opens the LAN URL → **Add to Home Screen**. That is a real home-screen app. Swap runs on the host engine.
4. The Swift folder is source for a future Mac build. It is not an installed IPA.

## GPU

Gateway has **no CUDA**. It only HTTP-proxies to the already-running MultoModa daemon. It does not start Jane, Ollama, or a second InsightFace process.
