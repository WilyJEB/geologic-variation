# retained-map-1: development display contract

Base merged PR59 5d007f5. Push this contract before implementation.
Immutable td-story.zip SHA256 fec51d36faeb1d8b99e7624c2daab5cbd2b614227c6df9527dfe0f7c7954da47.
Members: input/visual-data.json 8dc1e0a9f98edd1dc6b2ce74cc1d795c117c15feb9503b0260a5c5ef23a701d6;
input/pr58-result.json d0853fba10ca350e353d9a2786a6362d99f80363aa7b12a071d470b89e56819c;
result.json 9caff8648cb2165bf0d0ed7c3e9fd70ce6759d28b0c891b9fd36de1551fac650.
Display unchanged PR58 terrain illustration and PR59 story, no replacement construction.

Native x,z map to Minecraft X=s*x,Z=s*z, with absolute origin unchanged,
no rotation/reflection/recentering of coordinates. Display scale s=1 or6 only;
not the loaded world's scale. Native pixel is one block at scale1, six at scale6.
Signed block ownership uses floor, chunk=floor(block/16), local=floorMod(block,16).
Query [x2688,5761) x [z10880,13953); final sites x5760,z13952.
Spacing64 becomes64/384 blocks; nominal2048 bands become2048/12288 blocks.
The query spans3073/18438 blocks per axis. Elevations stay TD metres, never
substitute Minecraft Y or fabricate terrain between/exterior to retained sites.

Probe source/resources only, excluded from production JAR. An opt-in title-screen
button opens a retained map Screen; no world/provider/settings APIs, no save writes,
no generation registration. Separate isolated desktop display of the same records
is allowed to avoid normal client startup inference. No Minecraft/TD launch is
needed or authorized here. Minecraft Screen compile verification is distinct from
isolated display verification. Do not imply records describe a loaded world.

Toggle baseline/story and scale; inspect actual nearest sample via click with
finite hit radius, never pretend arbitrary map clicks have observed heights.
Show original query footprint, conceptual contact polylines, stable IDs, sites,
missing support, block/chunk distances and selected sample's shared surface/deep
story. Distinguish seed choices, measured descriptors, authored interpretation,
and uncertainty. Preserve PR59 negative contact judgment.

Fixed2401 sites, <=7 regional cards, <=512 contact segments, <=2MiB input;
no network, cache growth, terrain access, flood-fill, background workers or disk
writes during inspection. One fixed viewport, no general rendering framework.
Portable deterministic resource/export plus coordinate-only and retained-record
checks: scale1/6, negatives/chunk edges, contact agreement, traversal independence,
shared identity, immutable hashes, finite bounds. Render same map in isolated route;
record visual judgment separately from computed checks and client verification.
No fresh seeds, TD, numerical experiments, parameter search or history replacement.

All PR54-59 validation/performance/adoption/save-safety gates carry forward.
Geology-1/production/guards/optional Ulti-World/continuing worlds remain unchanged.
#9/#11 open. PR54 four launches exhausted, executed4a2fa1c; final capture mixin
compile-verified only; historical arrays/indices/ULPs unavailable. All frozen
failures stay failed. Preserve viewer repairs and unrelated temp. Passing CI before
merge; strict retained/new exports after final Windows checkout.
