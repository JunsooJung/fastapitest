<script>
    import fastapi from "../lib/api"
    import Error from "../components/Error.svelte"
    import { push } from "svelte-spa-router"
    import { is_login, username } from "../lib/store"
    import { onMount } from "svelte"

    // Error.svelte 와 호환되게 기본값 제공
    let error = { detail: "" }

    // 시작 버튼 / 제시어 / 입력값 상태
    let isRunning = false
    let promptText = "시작 버튼을 누르면 제시어가 표시됩니다."
    let detectedText = ""

    // 랭킹 (일단 더미, 나중에 백엔드 연동)
    let ranking = [
        { rank: 1, user: "예시 사용자", score: 120, time: "00:45" },
        { rank: 2, user: "SampleUser", score: 95, time: "01:02" },
    ]

    // TODO: 나중에 /api/keyboard/ranking 구현 후 호출
    // function loadRanking() {
    //     fastapi(
    //         "get",
    //         "/api/keyboard/ranking",
    //         null,
    //         (json) => {
    //             ranking = json
    //         },
    //         (err) => {
    //             error = err
    //         }
    //     )
    // }

    // onMount(() => {
    //     loadRanking()
    // })

    const handleStart = () => {
        // 로그인 안 되어 있으면 로그인 페이지로 보낼지 여부 (선택사항)
        if (!$is_login) {
            if (confirm("로그인이 필요한 기능입니다. 로그인 페이지로 이동할까요?")) {
                push("/user-login")
            }
            return
        }

        // 백엔드: /api/keyboard/start → run_keyboard_session() 백그라운드 실행
        fastapi(
            "post",
            "/api/keyboard/start",
            {},  // body 없음
            (json) => {
                console.log("keyboard/start 응답:", json)
                // 나중에 여기서 json.prompt, json.session_id 등을 받아서 저장하면 됨
                isRunning = true
                promptText = json.prompt || "랜덤 제시어가 여기에 표시됩니다."
            },
            (err) => {
                error = err
            }
        )
    }
</script>

<Error {error} />

<div class="container py-4">

    <!-- 상단 제목 영역 -->
    <div class="d-flex justify-content-between align-items-center mb-3">
        <div>
            <h1 class="h4 fw-bold mb-1">가상 키보드 연습</h1>
            <div class="text-muted small">
                웹캠 + 가상 키보드 레이아웃 + 랭킹 시스템
            </div>
        </div>
        {#if $is_login}
            <div class="text-end small text-muted">
                <div><strong>{$username}</strong> 님</div>
                <div>세션이 시작되면 로컬에서 웹캠 프로그램이 실행됩니다.</div>
            </div>
        {:else}
            <div class="text-end small text-danger">
                로그인 후 시작할 수 있습니다.
            </div>
        {/if}
    </div>

    <!-- 1. 웹캠 / 가상 키보드 영역 -->
    <div class="row g-4 mb-4">
        <!-- 웹캠 -->
        <div class="col-md-6">
            <div class="kb-panel">
                <div class="kb-panel-title">웹캠</div>
                <div class="kb-panel-body p-0">
                    <img
                        src="http://127.0.0.1:8000/api/keyboard/stream"
                        alt="Webcam stream"
                        class="kb-video"
                    />
                </div>
            </div>
        </div>

        <!-- 가상 키보드 -->
        <div class="col-md-6">
            <div class="kb-panel">
                <div class="kb-panel-title">가상 키보드</div>
                <div class="kb-panel-body text-muted small">
                    가상 키보드 레이아웃이 들어올 영역입니다.<br />
                    (현재는 시각화만 로컬 cv2 창에서 처리됩니다.)
                </div>
            </div>
        </div>
    </div>

    <!-- 2. 시작 버튼 / 제시어 + 입력창 -->
    {#if !isRunning}
        <div class="text-center mb-5">
            <button
                class="btn btn-outline-dark rounded-pill px-4 py-2"
                on:click={handleStart}
            >
                시작하기
            </button>
            <div class="mt-2 text-muted small">
                시작 버튼을 누르면 백엔드에서 웹캠 프로그램이 실행되고,<br />
                이 영역은 제시어/입력창 UI로 전환됩니다.
            </div>
        </div>
    {:else}
        <div class="row justify-content-center mb-5">
            <div class="col-md-8">

                <!-- 제시어 -->
                <div class="kb-pill mb-3">
                    <div class="kb-pill-label">제시어</div>
                    <div class="kb-pill-content fw-semibold">
                        {promptText}
                    </div>
                </div>

                <!-- 입력창 (카메라 인식 결과 텍스트) -->
                <div class="kb-pill">
                    <div class="kb-pill-label">입력창</div>
                    <input
                        type="text"
                        class="form-control border-0 p-0 pt-1 kb-input"
                        bind:value={detectedText}
                        placeholder="카메라 동작을 기반으로 인식된 텍스트가 들어올 영역"
                    />
                </div>

            </div>
        </div>
    {/if}

    <hr class="my-4" />

    <!-- 3. 랭킹 테이블 -->
    <section class="mb-4">
        <h2 class="h5 mb-3">랭킹</h2>
        <div class="kb-ranking table-responsive">
            <table class="table table-sm align-middle mb-0">
                <thead class="table-light">
                    <tr>
                        <th scope="col">순위</th>
                        <th scope="col">사용자</th>
                        <th scope="col">점수</th>
                        <th scope="col">기록 시간</th>
                    </tr>
                </thead>
                <tbody>
                    {#each ranking as row}
                        <tr>
                            <td>{row.rank}</td>
                            <td>{row.user}</td>
                            <td>{row.score}</td>
                            <td>{row.time}</td>
                        </tr>
                    {/each}
                    <tr>
                        <td colspan="4" class="text-center text-muted">
                            ※ 현재는 더미 데이터입니다. /api/keyboard/ranking 구현 후 실제 랭킹을 불러옵니다.
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </section>

</div>

<style>
    .kb-panel {
        border-radius: 24px;
        border: 2px solid #000;
        background-color: #f5f5f5;
        min-height: 220px;
        padding: 1rem 1.25rem;
        display: flex;
        flex-direction: column;
    }

    .kb-panel-title {
        font-weight: 600;
        margin-bottom: 0.5rem;
    }

    .kb-panel-body {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
    }
    
    .kb-video {
        width: 100%;
        height: 100%;
        object-fit: cover;  /* or contain, 원하시는 형태로 */
        border-radius: 16px;
    }

    .kb-pill {
        border-radius: 999px;
        border: 2px dotted #999;
        padding: 0.75rem 1.75rem;
        background-color: #fafafa;
    }

    .kb-pill-label {
        font-size: 0.8rem;
        color: #777;
        margin-bottom: 0.15rem;
    }

    .kb-pill-content {
        font-size: 1rem;
    }

    .kb-input:focus {
        box-shadow: none;
        outline: none;
    }

    .kb-ranking {
        border-radius: 24px;
        border: 2px solid #000;
        padding: 1rem;
        background-color: #fff;
    }
</style>
