# Milestone 1.4 Model Router

Status: M1.4 provider-neutral model boundary. The root architecture documents remain authoritative.

## Purpose and ownership

The Model Router under `deeplearn.core.models` owns provider-neutral model request/result types, explicit adapter registration, deterministic selection, adapter invocation, and safe failure normalization. It does not own agent-runtime orchestration, permission policy, tools, audit persistence, or vertical logic.

The canonical wire contracts are `contracts/v1/model-request.schema.json`, `model-result.schema.json`, and `model-error.schema.json`. Frozen Python values represent those concepts within the owned models boundary. Neither representation exposes provider SDK types or raw responses.

## Request, result, and capabilities

`ModelRequest` carries a request ID, the controlled `text_generation` capability, normalized text input, correlation and optional trace IDs, a timeout, and a maximum output-unit bound. It requests a capability rather than a provider or concrete model.

`ModelResult` records success or a normalized failure, selected provider/model/version when available, synthetic or adapter-reported latency, provider-neutral input/output/total usage counters, and correlation/trace identifiers. Provider identity fields are null when selection never occurred.

`ModelCapability` is defined once in the shared Core contracts boundary and reused by both the agent registry and models module. M1.4 adds no capabilities beyond `text_generation`.

## Adapter and deterministic selection

`ModelAdapter` exposes provider/model identity, supported capabilities, and one provider-neutral invocation method. Adapters register explicitly. A duplicate provider/model pair is rejected. The router selects the first eligible adapter in registration order; there is no weighting, pricing, health, geographic, or marketplace behavior.

The offline fake adapter identifies itself as `test.fake` / `test.fake-text` / `1.0.0`. It returns `fake:` followed by the normalized input, bounded by `max_output_units`. Its default latency is the fixed synthetic value 7 ms. Usage is synthetic character counting: input length, output length, and their sum. These values do not imitate provider billing semantics.

## Normalized failures

The model-owned error contract distinguishes `unsupported_capability`, `provider_unavailable`, `provider_failure`, `provider_timeout`, and `invalid_model_request`. Adapter exceptions are converted to bounded messages and stable codes; raw exception text, stack traces, credentials, and provider response objects do not cross the models boundary. The fake adapter has deterministic unavailable, failure, and timeout modes for offline tests.

## Provider neutrality and deferred work

Tests substitute a second fake provider while retaining the same request and router API, demonstrating that provider replacement requires no runtime or domain change. M1.4 performs no network access and adds no application dependency.

No real provider integration exists in M1.4. Provider SDKs, credentials, real-provider selection, failover, configuration services, runtime orchestration, safe tools, permission policy, audit/idempotency persistence, and all M1.5-or-later work remain deferred.
