<script>
    import fastapi from "../lib/api"
    import Error from "../components/Error.svelte"
    import { link, push } from 'svelte-spa-router'
    import { page, is_login, username } from "../lib/store"
    import moment from "moment/min/moment-with-locales"
    moment.locale('ko')
</script>

<div class="container py-5">

  <!-- 프로젝트 제목 영역 -->
  <div class="text-center mb-5">
    <h1 class="display-4 fw-bold mb-3">가상 키보드 구현 및 앱 퍼블리싱</h1>
    <p class="fs-5 text-muted">
      MBC 아카데미 AI심화 과정 팀 프로젝트
    </p>
  </div>

  <!-- 프로젝트 내용 설명 박스 -->
  <div class="row justify-content-center mb-4">
    <div class="col-md-8">
      <div class="p-5 bg-light border rounded-4">
        <h2 class="h4 text-center mb-3">프로젝트 내용 설명</h2>
        <p class="text-muted mb-0 text-center">
          • 이 프로젝트가 무엇을 하는지  
          • 어떤 기술 스택(FastAPI, Svelte, MySQL 등)을 쓰는지  
          • 사용자가 이 서비스를 통해 무엇을 할 수 있는지  
          를 간단히 적어두는 영역입니다.
        </p>
      </div>
    </div>
  </div>

  <!-- 로그인 / 회원가입 영역 (초록 박스) -->
  <div class="row justify-content-center">
    <div class="col-md-4">
      <div class="p-4 rounded-4 text-center" style="background-color:#4CAF50; color:white;">
        {#if $is_login}
          <p class="mb-3">
            <strong>{$username}</strong> 님, 환영합니다.
          </p>
          <a use:link href="/keyboard" class="btn btn-light w-100 mb-2">
            키보드 바로가기
          </a>
          <a use:link href="/board" class="btn btn-outline-light w-100">
            게시판 바로가기
          </a>
        {:else}
          <p class="mb-3">
            로그인 / 회원가입 창 영역
          </p>
          <a use:link href="/user-login" class="btn btn-light w-100 mb-2">
            로그인
          </a>
          <a use:link href="/user-create" class="btn btn-outline-light w-100">
            회원가입
          </a>
        {/if}
      </div>
    </div>
  </div>

</div>
