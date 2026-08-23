"""Interface web da aplicação de previsão de churn."""

from fastapi.responses import HTMLResponse


HTML_PAGE = """
<!DOCTYPE html>
<html lang="pt-BR">

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>Customer Churn AI</title>

    <style>

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        :root {
            --primary: #2563eb;
            --primary-dark: #1d4ed8;
            --primary-light: #eff6ff;

            --background: #f5f7fb;
            --surface: #ffffff;
            --surface-soft: #f8fafc;

            --text: #0f172a;
            --text-secondary: #475569;
            --muted: #64748b;

            --border: #e2e8f0;

            --success: #16a34a;
            --success-bg: #f0fdf4;

            --danger: #dc2626;
            --danger-bg: #fef2f2;

            --warning: #d97706;
            --warning-bg: #fffbeb;

            --sidebar: #0b1220;
            --sidebar-secondary: #111c30;

            --shadow-sm:
                0 1px 2px rgba(15, 23, 42, 0.04);

            --shadow:
                0 10px 30px rgba(15, 23, 42, 0.06);

            --shadow-lg:
                0 25px 60px rgba(15, 23, 42, 0.12);
        }


        /* =========================================================
           BASE
        ========================================================= */

        body {

            font-family:
                Inter,
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                Arial,
                sans-serif;

            background: var(--background);

            color: var(--text);

            min-height: 100vh;

            line-height: 1.5;
        }


        button,
        input,
        select {

            font-family: inherit;
        }


        button {

            border: none;
        }


        /* =========================================================
           LOGIN
        ========================================================= */

        #loginPage {

            min-height: 100vh;

            display: flex;

            align-items: center;

            justify-content: center;

            padding: 24px;

            background:
                radial-gradient(
                    circle at 15% 20%,
                    rgba(37, 99, 235, 0.15),
                    transparent 32%
                ),
                radial-gradient(
                    circle at 85% 80%,
                    rgba(30, 64, 175, 0.12),
                    transparent 30%
                ),
                #f8fafc;
        }


        .login-wrapper {

            width: 100%;

            max-width: 440px;
        }


        .login-brand {

            text-align: center;

            margin-bottom: 24px;
        }


        .login-logo {

            width: 72px;

            height: 72px;

            margin: 0 auto 18px;

            border-radius: 20px;

            display: flex;

            align-items: center;

            justify-content: center;

            background:
                linear-gradient(
                    135deg,
                    #2563eb,
                    #1e40af
                );

            color: white;

            font-size: 32px;

            box-shadow:
                0 15px 35px
                rgba(37, 99, 235, 0.25);
        }


        .login-brand h1 {

            font-size: 28px;

            font-weight: 800;

            letter-spacing: -0.7px;
        }


        .login-brand p {

            margin-top: 6px;

            color: var(--muted);

            font-size: 14px;
        }


        .login-card {

            background: white;

            border:
                1px solid
                rgba(226, 232, 240, 0.9);

            border-radius: 22px;

            padding: 34px;

            box-shadow: var(--shadow-lg);
        }


        .login-card-header {

            margin-bottom: 26px;
        }


        .login-card-header h2 {

            font-size: 20px;

            margin-bottom: 5px;
        }


        .login-card-header p {

            color: var(--muted);

            font-size: 13px;
        }


        .field {

            margin-bottom: 18px;
        }


        .field label {

            display: block;

            margin-bottom: 7px;

            font-size: 13px;

            font-weight: 600;

            color: #334155;
        }


        .field input {

            width: 100%;

            height: 48px;

            border:
                1px solid
                var(--border);

            border-radius: 10px;

            padding: 0 14px;

            font-size: 14px;

            background: #fff;

            transition:
                border-color .2s,
                box-shadow .2s;
        }


        .field input:focus {

            outline: none;

            border-color: var(--primary);

            box-shadow:
                0 0 0 4px
                rgba(37, 99, 235, .09);
        }


        .login-button {

            width: 100%;

            height: 49px;

            margin-top: 6px;

            border-radius: 10px;

            background:
                linear-gradient(
                    135deg,
                    var(--primary),
                    var(--primary-dark)
                );

            color: white;

            font-size: 14px;

            font-weight: 700;

            cursor: pointer;

            transition:
                transform .2s,
                box-shadow .2s;
        }


        .login-button:hover {

            transform: translateY(-1px);

            box-shadow:
                0 10px 25px
                rgba(37, 99, 235, .22);
        }


        .login-button:disabled {

            opacity: .7;

            cursor: wait;

            transform: none;

            box-shadow: none;
        }


        .login-error {

            display: none;

            margin-top: 16px;

            padding: 12px 14px;

            border-radius: 9px;

            background: var(--danger-bg);

            border:
                1px solid
                #fecaca;

            color: var(--danger);

            font-size: 13px;
        }


        .login-error.visible {

            display: block;
        }


        .login-footer {

            text-align: center;

            margin-top: 22px;

            color: #94a3b8;

            font-size: 11px;
        }


        /* =========================================================
           APPLICATION
        ========================================================= */

        #appPage {

            display: none;

            min-height: 100vh;
        }


        #appPage.visible {

            display: flex;
        }


        /* =========================================================
           SIDEBAR
        ========================================================= */

        .sidebar {

            width: 250px;

            min-height: 100vh;

            background:
                linear-gradient(
                    180deg,
                    #0b1220,
                    #0f172a
                );

            color: white;

            position: fixed;

            left: 0;

            top: 0;

            bottom: 0;

            display: flex;

            flex-direction: column;

            z-index: 20;
        }


        .sidebar-brand {

            height: 82px;

            padding: 0 24px;

            display: flex;

            align-items: center;

            gap: 12px;

            border-bottom:
                1px solid
                rgba(255,255,255,.07);
        }


        .sidebar-logo {

            width: 40px;

            height: 40px;

            border-radius: 11px;

            display: flex;

            align-items: center;

            justify-content: center;

            background:
                linear-gradient(
                    135deg,
                    #2563eb,
                    #1d4ed8
                );

            font-size: 20px;
        }


        .sidebar-brand-text strong {

            display: block;

            font-size: 14px;
        }


        .sidebar-brand-text span {

            display: block;

            color: #64748b;

            font-size: 10px;

            margin-top: 2px;
        }


        .sidebar-section {

            padding: 24px 14px 8px;

            color: #64748b;

            text-transform: uppercase;

            font-size: 10px;

            font-weight: 700;

            letter-spacing: .8px;
        }


        .sidebar-menu {

            padding: 0 12px;
        }


        .sidebar-item {

            width: 100%;

            display: flex;

            align-items: center;

            gap: 12px;

            padding: 11px 12px;

            margin-bottom: 4px;

            border-radius: 9px;

            background: transparent;

            color: #94a3b8;

            text-align: left;

            font-size: 13px;

            cursor: pointer;

            transition:
                background .2s,
                color .2s;
        }


        .sidebar-item:hover {

            background:
                rgba(255,255,255,.05);

            color: white;
        }


        .sidebar-item.active {

            background:
                rgba(37,99,235,.18);

            color: #bfdbfe;
        }


        .sidebar-item-icon {

            width: 20px;

            text-align: center;

            font-size: 16px;
        }


        .sidebar-footer {

            margin-top: auto;

            padding: 16px;

            border-top:
                1px solid
                rgba(255,255,255,.07);
        }


        .user-mini {

            display: flex;

            align-items: center;

            gap: 10px;

            margin-bottom: 12px;
        }


        .user-avatar {

            width: 34px;

            height: 34px;

            border-radius: 50%;

            display: flex;

            align-items: center;

            justify-content: center;

            background:
                #1e3a8a;

            color: #bfdbfe;

            font-size: 13px;

            font-weight: 700;
        }


        .user-info {

            overflow: hidden;
        }


        .user-info strong {

            display: block;

            color: white;

            font-size: 12px;

            white-space: nowrap;

            overflow: hidden;

            text-overflow: ellipsis;
        }


        .user-info span {

            display: block;

            color: #64748b;

            font-size: 10px;
        }


        .logout-button {

            width: 100%;

            height: 36px;

            border-radius: 8px;

            background:
                rgba(255,255,255,.05);

            color: #94a3b8;

            cursor: pointer;

            font-size: 11px;

            transition: .2s;
        }


        .logout-button:hover {

            background:
                rgba(220,38,38,.12);

            color: #fca5a5;
        }


        /* =========================================================
           MAIN
        ========================================================= */

        .main {

            margin-left: 250px;

            width: calc(100% - 250px);

            min-height: 100vh;
        }


        .topbar {

            height: 82px;

            background: white;

            border-bottom:
                1px solid
                var(--border);

            display: flex;

            align-items: center;

            justify-content: space-between;

            padding: 0 38px;

            position: sticky;

            top: 0;

            z-index: 10;
        }


        .topbar-title h1 {

            font-size: 18px;

            font-weight: 700;

            letter-spacing: -.2px;
        }


        .topbar-title p {

            color: var(--muted);

            font-size: 11px;

            margin-top: 2px;
        }


        .status {

            display: flex;

            align-items: center;

            gap: 8px;

            padding: 7px 11px;

            border-radius: 20px;

            background:
                var(--success-bg);

            color:
                var(--success);

            font-size: 11px;

            font-weight: 600;
        }


        .status-dot {

            width: 7px;

            height: 7px;

            border-radius: 50%;

            background: var(--success);
        }


        .content {

            max-width: 1250px;

            margin: 0 auto;

            padding: 32px 38px 60px;
        }


        /* =========================================================
           DASHBOARD INTRO
        ========================================================= */

        .page-heading {

            display: flex;

            justify-content: space-between;

            align-items: flex-end;

            margin-bottom: 25px;
        }


        .page-heading h2 {

            font-size: 27px;

            letter-spacing: -.6px;
        }


        .page-heading p {

            color: var(--muted);

            font-size: 13px;

            margin-top: 5px;
        }


        .model-badge {

            display: flex;

            align-items: center;

            gap: 8px;

            padding: 8px 12px;

            background: white;

            border:
                1px solid
                var(--border);

            border-radius: 8px;

            color: var(--text-secondary);

            font-size: 11px;

            box-shadow: var(--shadow-sm);
        }


        .model-badge span {

            color: var(--primary);

            font-weight: 700;
        }


        /* =========================================================
           STATS
        ========================================================= */

        .stats {

            display: grid;

            grid-template-columns:
                repeat(3, 1fr);

            gap: 16px;

            margin-bottom: 24px;
        }


        .stat-card {

            background: white;

            border:
                1px solid
                var(--border);

            border-radius: 13px;

            padding: 18px;

            box-shadow: var(--shadow-sm);

            display: flex;

            align-items: center;

            gap: 14px;
        }


        .stat-icon {

            width: 42px;

            height: 42px;

            border-radius: 10px;

            display: flex;

            align-items: center;

            justify-content: center;

            font-size: 18px;
        }


        .stat-icon.blue {

            background: #eff6ff;
        }


        .stat-icon.green {

            background: #f0fdf4;
        }


        .stat-icon.purple {

            background: #faf5ff;
        }


        .stat-label {

            color: var(--muted);

            font-size: 10px;

            text-transform: uppercase;

            letter-spacing: .5px;

            font-weight: 600;
        }


        .stat-value {

            margin-top: 2px;

            font-size: 18px;

            font-weight: 750;
        }


        /* =========================================================
           CARDS
        ========================================================= */

        .card {

            background: white;

            border:
                1px solid
                var(--border);

            border-radius: 14px;

            box-shadow: var(--shadow-sm);

            margin-bottom: 18px;

            overflow: hidden;
        }


        .card-header {

            min-height: 68px;

            padding: 16px 20px;

            border-bottom:
                1px solid
                var(--border);

            display: flex;

            align-items: center;

            gap: 12px;
        }


        .card-icon {

            width: 36px;

            height: 36px;

            border-radius: 9px;

            background: var(--primary-light);

            color: var(--primary);

            display: flex;

            align-items: center;

            justify-content: center;

            font-size: 16px;
        }


        .card-title h3 {

            font-size: 14px;

            font-weight: 700;
        }


        .card-title p {

            color: var(--muted);

            font-size: 11px;

            margin-top: 2px;
        }


        .card-body {

            padding: 21px;
        }


        /* =========================================================
           FORM
        ========================================================= */

        .form-grid {

            display: grid;

            grid-template-columns:
                repeat(3, 1fr);

            gap: 17px;
        }


        .form-group {

            display: flex;

            flex-direction: column;
        }


        .form-group label {

            color: #334155;

            font-size: 11px;

            font-weight: 650;

            margin-bottom: 6px;
        }


        .form-group input,
        .form-group select {

            width: 100%;

            height: 42px;

            border:
                1px solid
                var(--border);

            border-radius: 8px;

            padding: 0 11px;

            background: white;

            color: var(--text);

            font-size: 12px;

            transition:
                border-color .2s,
                box-shadow .2s;
        }


        .form-group input:hover,
        .form-group select:hover {

            border-color: #cbd5e1;
        }


        .form-group input:focus,
        .form-group select:focus {

            outline: none;

            border-color:
                var(--primary);

            box-shadow:
                0 0 0 3px
                rgba(37,99,235,.08);
        }


        .section-title {

            grid-column: 1 / -1;

            margin-top: 5px;

            padding-bottom: 7px;

            border-bottom:
                1px solid
                #eef2f7;

            color: #94a3b8;

            font-size: 10px;

            font-weight: 750;

            text-transform: uppercase;

            letter-spacing: .7px;
        }


        /* =========================================================
           ACTION
        ========================================================= */

        .form-action {

            display: flex;

            justify-content: flex-end;

            align-items: center;

            gap: 15px;

            margin-top: 24px;

            padding-top: 18px;

            border-top:
                1px solid
                var(--border);
        }


        .form-hint {

            color: #94a3b8;

            font-size: 10px;

            margin-right: auto;
        }


        .predict-button {

            min-width: 210px;

            height: 46px;

            padding: 0 22px;

            border-radius: 9px;

            background:
                linear-gradient(
                    135deg,
                    #2563eb,
                    #1d4ed8
                );

            color: white;

            font-size: 12px;

            font-weight: 700;

            cursor: pointer;

            box-shadow:
                0 8px 18px
                rgba(37,99,235,.18);

            transition:
                transform .2s,
                box-shadow .2s;
        }


        .predict-button:hover {

            transform: translateY(-1px);

            box-shadow:
                0 11px 23px
                rgba(37,99,235,.25);
        }


        .predict-button:disabled {

            background: #94a3b8;

            cursor: wait;

            box-shadow: none;

            transform: none;
        }


        /* =========================================================
           RESULT
        ========================================================= */

        #resultCard {

            display: none;
        }


        #resultCard.visible {

            display: block;

            animation:
                resultIn .35s ease;
        }


        @keyframes resultIn {

            from {

                opacity: 0;

                transform:
                    translateY(10px);
            }

            to {

                opacity: 1;

                transform:
                    translateY(0);
            }
        }


        .result-body {

            padding: 21px;
        }


        .result-main {

            display: grid;

            grid-template-columns:
                1fr 280px;

            gap: 18px;
        }


        .prediction-box {

            border-radius: 13px;

            padding: 25px;

            border:
                1px solid
                #dbeafe;

            background:
                linear-gradient(
                    135deg,
                    #eff6ff,
                    #f8fafc
                );
        }


        .prediction-label {

            color: var(--muted);

            font-size: 10px;

            text-transform: uppercase;

            letter-spacing: .7px;

            font-weight: 700;

            margin-bottom: 7px;
        }


        #predictionValue {

            font-size: 31px;

            font-weight: 800;

            letter-spacing: -.7px;

            color: var(--primary);
        }


        #predictionDescription {

            margin-top: 7px;

            color: var(--text-secondary);

            font-size: 12px;

            max-width: 700px;
        }


        .risk-indicator {

            border-radius: 13px;

            padding: 20px;

            background:
                var(--surface-soft);

            border:
                1px solid
                var(--border);

            text-align: center;
        }


        .risk-title {

            color: var(--muted);

            font-size: 10px;

            text-transform: uppercase;

            font-weight: 700;

            letter-spacing: .6px;

            margin-bottom: 12px;
        }


        .risk-circle {

            width: 82px;

            height: 82px;

            border-radius: 50%;

            margin: 0 auto 10px;

            display: flex;

            align-items: center;

            justify-content: center;

            background:
                #eff6ff;

            color: var(--primary);

            border:
                7px solid
                #dbeafe;

            font-size: 15px;

            font-weight: 800;
        }


        #riskText {

            font-size: 11px;

            color: var(--muted);
        }


        .raw-section {

            margin-top: 18px;
        }


        .raw-title {

            color: var(--text-secondary);

            font-size: 11px;

            font-weight: 700;

            margin-bottom: 7px;
        }


        .raw-result {

            background:
                #0b1220;

            color:
                #cbd5e1;

            padding: 16px;

            border-radius: 10px;

            overflow-x: auto;

            font-family:
                Consolas,
                Monaco,
                monospace;

            font-size: 11px;

            line-height: 1.6;

            max-height: 260px;
        }


        /* =========================================================
           MOBILE
        ========================================================= */

        @media (max-width: 1000px) {

            .sidebar {

                width: 210px;
            }

            .main {

                margin-left: 210px;

                width:
                    calc(100% - 210px);
            }

            .form-grid {

                grid-template-columns:
                    repeat(2, 1fr);
            }

            .result-main {

                grid-template-columns: 1fr;
            }
        }


        @media (max-width: 760px) {

            .sidebar {

                position: static;

                width: 100%;

                min-height: auto;

                display: none;
            }

            .main {

                margin-left: 0;

                width: 100%;
            }

            .topbar {

                padding: 0 18px;
            }

            .content {

                padding:
                    22px 16px 40px;
            }

            .page-heading {

                display: block;
            }

            .model-badge {

                display: inline-flex;

                margin-top: 14px;
            }

            .stats {

                grid-template-columns: 1fr;
            }

            .form-grid {

                grid-template-columns: 1fr;
            }

            .form-action {

                display: block;
            }

            .form-hint {

                display: block;

                margin-bottom: 12px;
            }

            .predict-button {

                width: 100%;
            }

            .login-card {

                padding: 27px 22px;
            }
        }

    </style>

</head>


<body>


<!-- =========================================================
     LOGIN
========================================================= -->

<section id="loginPage">

    <div class="login-wrapper">

        <div class="login-brand">

            <div class="login-logo">
                📊
            </div>

            <h1>
                Customer Churn AI
            </h1>

            <p>
                Inteligência aplicada à retenção de clientes
            </p>

        </div>


        <div class="login-card">

            <div class="login-card-header">

                <h2>
                    Acesso ao sistema
                </h2>

                <p>
                    Entre com suas credenciais para continuar.
                </p>

            </div>


            <form id="loginForm">

                <div class="field">

                    <label for="username">
                        Usuário
                    </label>

                    <input
                        id="username"
                        name="username"
                        type="text"
                        placeholder="Digite seu usuário"
                        autocomplete="username"
                        required
                    >

                </div>


                <div class="field">

                    <label for="password">
                        Senha
                    </label>

                    <input
                        id="password"
                        name="password"
                        type="password"
                        placeholder="Digite sua senha"
                        autocomplete="current-password"
                        required
                    >

                </div>


                <button
                    type="submit"
                    id="loginButton"
                    class="login-button"
                >
                    Entrar no sistema
                </button>


                <div
                    id="loginError"
                    class="login-error"
                ></div>

            </form>

        </div>


        <div class="login-footer">

            Customer Churn AI · Machine Learning Platform

        </div>

    </div>

</section>



<!-- =========================================================
     APPLICATION
========================================================= -->

<section id="appPage">


    <!-- SIDEBAR -->

    <aside class="sidebar">


        <div class="sidebar-brand">

            <div class="sidebar-logo">
                📊
            </div>

            <div class="sidebar-brand-text">

                <strong>
                    Customer Churn
                </strong>

                <span>
                    AI PLATFORM
                </span>

            </div>

        </div>


        <div class="sidebar-section">
            Plataforma
        </div>


        <div class="sidebar-menu">

            <button
                class="sidebar-item active"
                type="button"
            >

                <span class="sidebar-item-icon">
                    ◈
                </span>

                <span>
                    Previsão de Churn
                </span>

            </button>


            <button
                class="sidebar-item"
                type="button"
            >

                <span class="sidebar-item-icon">
                    ◫
                </span>

                <span>
                    Análise de clientes
                </span>

            </button>


            <button
                class="sidebar-item"
                type="button"
            >

                <span class="sidebar-item-icon">
                    ◉
                </span>

                <span>
                    Modelo preditivo
                </span>

            </button>

        </div>


        <div class="sidebar-section">
            Sistema
        </div>


        <div class="sidebar-menu">

            <button
                class="sidebar-item"
                type="button"
            >

                <span class="sidebar-item-icon">
                    ⚙
                </span>

                <span>
                    Configurações
                </span>

            </button>

        </div>


        <div class="sidebar-footer">

            <div class="user-mini">

                <div
                    class="user-avatar"
                    id="userAvatar"
                >
                    U
                </div>

                <div class="user-info">

                    <strong id="loggedUser">
                        Usuário
                    </strong>

                    <span>
                        Usuário autenticado
                    </span>

                </div>

            </div>


            <button
                id="logoutButton"
                class="logout-button"
            >
                Sair da plataforma
            </button>

        </div>

    </aside>



    <!-- MAIN -->

    <main class="main">


        <!-- TOPBAR -->

        <header class="topbar">

            <div class="topbar-title">

                <h1>
                    Customer Churn AI
                </h1>

                <p>
                    Sistema inteligente de previsão de cancelamento
                </p>

            </div>


            <div class="status">

                <span class="status-dot"></span>

                Modelo disponível

            </div>

        </header>



        <!-- CONTENT -->

        <div class="content">


            <!-- PAGE HEADER -->

            <div class="page-heading">

                <div>

                    <h2>
                        Previsão de Churn
                    </h2>

                    <p>
                        Analise o perfil do cliente e estime a probabilidade de cancelamento.
                    </p>

                </div>


                <div class="model-badge">

                    Modelo:
                    <span>
                        Customer Churn ML
                    </span>

                </div>

            </div>



            <!-- STATS -->

            <div class="stats">

                <div class="stat-card">

                    <div class="stat-icon blue">
                        🤖
                    </div>

                    <div>

                        <div class="stat-label">
                            Tipo de análise
                        </div>

                        <div class="stat-value">
                            Predição
                        </div>

                    </div>

                </div>


                <div class="stat-card">

                    <div class="stat-icon green">
                        ⚡
                    </div>

                    <div>

                        <div class="stat-label">
                            Processamento
                        </div>

                        <div class="stat-value">
                            Automático
                        </div>

                    </div>

                </div>


                <div class="stat-card">

                    <div class="stat-icon purple">
                        🎯
                    </div>

                    <div>

                        <div class="stat-label">
                            Objetivo
                        </div>

                        <div class="stat-value">
                            Retenção
                        </div>

                    </div>

                </div>

            </div>



            <!-- =================================================
                 PERFIL
            ================================================= -->

            <form id="predictionForm">


                <div class="card">

                    <div class="card-header">

                        <div class="card-icon">
                            👤
                        </div>

                        <div class="card-title">

                            <h3>
                                Perfil do cliente
                            </h3>

                            <p>
                                Informações demográficas e relacionamento
                            </p>

                        </div>

                    </div>


                    <div class="card-body">

                        <div class="form-grid">


                            <div class="form-group">

                                <label for="gender">
                                    Gênero
                                </label>

                                <select
                                    id="gender"
                                    required
                                >

                                    <option value="">
                                        Selecione
                                    </option>

                                    <option value="Female">
                                        Feminino
                                    </option>

                                    <option value="Male">
                                        Masculino
                                    </option>

                                </select>

                            </div>


                            <div class="form-group">

                                <label for="SeniorCitizen">
                                    Senior Citizen
                                </label>

                                <select
                                    id="SeniorCitizen"
                                    required
                                >

                                    <option value="">
                                        Selecione
                                    </option>

                                    <option value="0">
                                        Não
                                    </option>

                                    <option value="1">
                                        Sim
                                    </option>

                                </select>

                            </div>


                            <div class="form-group">

                                <label for="Partner">
                                    Possui parceiro?
                                </label>

                                <select
                                    id="Partner"
                                    required
                                >

                                    <option value="">
                                        Selecione
                                    </option>

                                    <option value="Yes">
                                        Sim
                                    </option>

                                    <option value="No">
                                        Não
                                    </option>

                                </select>

                            </div>


                            <div class="form-group">

                                <label for="Dependents">
                                    Possui dependentes?
                                </label>

                                <select
                                    id="Dependents"
                                    required
                                >

                                    <option value="">
                                        Selecione
                                    </option>

                                    <option value="Yes">
                                        Sim
                                    </option>

                                    <option value="No">
                                        Não
                                    </option>

                                </select>

                            </div>


                            <div class="form-group">

                                <label for="tenure">
                                    Tempo como cliente
                                </label>

                                <input
                                    type="number"
                                    id="tenure"
                                    min="0"
                                    placeholder="Ex.: 12"
                                    required
                                >

                            </div>


                        </div>

                    </div>

                </div>



                <!-- =================================================
                     SERVIÇOS
                ================================================= -->

                <div class="card">

                    <div class="card-header">

                        <div class="card-icon">
                            📱
                        </div>

                        <div class="card-title">

                            <h3>
                                Serviços contratados
                            </h3>

                            <p>
                                Produtos e serviços utilizados pelo cliente
                            </p>

                        </div>

                    </div>


                    <div class="card-body">

                        <div class="form-grid">


                            <div class="form-group">

                                <label for="PhoneService">
                                    Serviço telefônico
                                </label>

                                <select
                                    id="PhoneService"
                                    required
                                >

                                    <option value="">
                                        Selecione
                                    </option>

                                    <option value="Yes">
                                        Sim
                                    </option>

                                    <option value="No">
                                        Não
                                    </option>

                                </select>

                            </div>


                            <div class="form-group">

                                <label for="MultipleLines">
                                    Múltiplas linhas
                                </label>

                                <select
                                    id="MultipleLines"
                                    required
                                >

                                    <option value="">
                                        Selecione
                                    </option>

                                    <option value="Yes">
                                        Sim
                                    </option>

                                    <option value="No">
                                        Não
                                    </option>

                                    <option value="No phone service">
                                        Sem serviço
                                    </option>

                                </select>

                            </div>


                            <div class="form-group">

                                <label for="InternetService">
                                    Serviço de internet
                                </label>

                                <select
                                    id="InternetService"
                                    required
                                >

                                    <option value="">
                                        Selecione
                                    </option>

                                    <option value="DSL">
                                        DSL
                                    </option>

                                    <option value="Fiber optic">
                                        Fibra óptica
                                    </option>

                                    <option value="No">
                                        Não possui
                                    </option>

                                </select>

                            </div>


                            <div class="section-title">
                                Serviços adicionais
                            </div>


                            <div class="form-group">

                                <label for="OnlineSecurity">
                                    Segurança online
                                </label>

                                <select
                                    id="OnlineSecurity"
                                    required
                                >

                                    <option value="">
                                        Selecione
                                    </option>

                                    <option value="Yes">
                                        Sim
                                    </option>

                                    <option value="No">
                                        Não
                                    </option>

                                    <option value="No internet service">
                                        Sem internet
                                    </option>

                                </select>

                            </div>


                            <div class="form-group">

                                <label for="OnlineBackup">
                                    Backup online
                                </label>

                                <select
                                    id="OnlineBackup"
                                    required
                                >

                                    <option value="">
                                        Selecione
                                    </option>

                                    <option value="Yes">
                                        Sim
                                    </option>

                                    <option value="No">
                                        Não
                                    </option>

                                    <option value="No internet service">
                                        Sem internet
                                    </option>

                                </select>

                            </div>


                            <div class="form-group">

                                <label for="DeviceProtection">
                                    Proteção de dispositivo
                                </label>

                                <select
                                    id="DeviceProtection"
                                    required
                                >

                                    <option value="">
                                        Selecione
                                    </option>

                                    <option value="Yes">
                                        Sim
                                    </option>

                                    <option value="No">
                                        Não
                                    </option>

                                    <option value="No internet service">
                                        Sem internet
                                    </option>

                                </select>

                            </div>


                            <div class="form-group">

                                <label for="TechSupport">
                                    Suporte técnico
                                </label>

                                <select
                                    id="TechSupport"
                                    required
                                >

                                    <option value="">
                                        Selecione
                                    </option>

                                    <option value="Yes">
                                        Sim
                                    </option>

                                    <option value="No">
                                        Não
                                    </option>

                                    <option value="No internet service">
                                        Sem internet
                                    </option>

                                </select>

                            </div>


                            <div class="form-group">

                                <label for="StreamingTV">
                                    Streaming TV
                                </label>

                                <select
                                    id="StreamingTV"
                                    required
                                >

                                    <option value="">
                                        Selecione
                                    </option>

                                    <option value="Yes">
                                        Sim
                                    </option>

                                    <option value="No">
                                        Não
                                    </option>

                                    <option value="No internet service">
                                        Sem internet
                                    </option>

                                </select>

                            </div>


                            <div class="form-group">

                                <label for="StreamingMovies">
                                    Streaming de filmes
                                </label>

                                <select
                                    id="StreamingMovies"
                                    required
                                >

                                    <option value="">
                                        Selecione
                                    </option>

                                    <option value="Yes">
                                        Sim
                                    </option>

                                    <option value="No">
                                        Não
                                    </option>

                                    <option value="No internet service">
                                        Sem internet
                                    </option>

                                </select>

                            </div>


                        </div>

                    </div>

                </div>



                <!-- =================================================
                     CONTRATO
                ================================================= -->

                <div class="card">

                    <div class="card-header">

                        <div class="card-icon">
                            💳
                        </div>

                        <div class="card-title">

                            <h3>
                                Contrato e pagamento
                            </h3>

                            <p>
                                Informações sobre contrato e forma de cobrança
                            </p>

                        </div>

                    </div>


                    <div class="card-body">

                        <div class="form-grid">


                            <div class="form-group">

                                <label for="Contract">
                                    Tipo de contrato
                                </label>

                                <select
                                    id="Contract"
                                    required
                                >

                                    <option value="">
                                        Selecione
                                    </option>

                                    <option value="Month-to-month">
                                        Mensal
                                    </option>

                                    <option value="One year">
                                        1 ano
                                    </option>

                                    <option value="Two year">
                                        2 anos
                                    </option>

                                </select>

                            </div>


                            <div class="form-group">

                                <label for="PaperlessBilling">
                                    Fatura digital
                                </label>

                                <select
                                    id="PaperlessBilling"
                                    required
                                >

                                    <option value="">
                                        Selecione
                                    </option>

                                    <option value="Yes">
                                        Sim
                                    </option>

                                    <option value="No">
                                        Não
                                    </option>

                                </select>

                            </div>


                            <div class="form-group">

                                <label for="PaymentMethod">
                                    Forma de pagamento
                                </label>

                                <select
                                    id="PaymentMethod"
                                    required
                                >

                                    <option value="">
                                        Selecione
                                    </option>

                                    <option value="Electronic check">
                                        Cheque eletrônico
                                    </option>

                                    <option value="Mailed check">
                                        Cheque enviado
                                    </option>

                                    <option value="Bank transfer (automatic)">
                                        Transferência automática
                                    </option>

                                    <option value="Credit card (automatic)">
                                        Cartão automático
                                    </option>

                                </select>

                            </div>


                        </div>

                    </div>

                </div>



                <!-- =================================================
                     FINANCEIRO
                ================================================= -->

                <div class="card">

                    <div class="card-header">

                        <div class="card-icon">
                            💰
                        </div>

                        <div class="card-title">

                            <h3>
                                Informações financeiras
                            </h3>

                            <p>
                                Valores associados ao relacionamento do cliente
                            </p>

                        </div>

                    </div>


                    <div class="card-body">

                        <div class="form-grid">


                            <div class="form-group">

                                <label for="MonthlyCharges">
                                    Cobrança mensal
                                </label>

                                <input
                                    type="number"
                                    id="MonthlyCharges"
                                    step="0.01"
                                    min="0"
                                    placeholder="Ex.: 1000.10"
                                    required
                                >

                            </div>


                            <div class="form-group">

                                <label for="TotalCharges">
                                    Total pago
                                </label>

                                <input
                                    type="number"
                                    id="TotalCharges"
                                    step="0.01"
                                    min="0"
                                    placeholder="Ex.: 2000.65"
                                    required
                                >

                            </div>


                        </div>


                        <div class="form-action">

                            <span class="form-hint">
                                Todos os campos são utilizados pelo modelo preditivo.
                            </span>

                            <button
                                type="submit"
                                id="predictButton"
                                class="predict-button"
                            >
                                🔍 Analisar cliente
                            </button>

                        </div>

                    </div>

                </div>


            </form>



            <!-- =================================================
                 RESULTADO
            ================================================= -->

            <div
                id="resultCard"
                class="card"
            >

                <div class="card-header">

                    <div class="card-icon">
                        🤖
                    </div>

                    <div class="card-title">

                        <h3>
                            Resultado da análise
                        </h3>

                        <p>
                            Resultado retornado pelo modelo de Machine Learning
                        </p>

                    </div>

                </div>


                <div class="result-body">


                    <div class="result-main">


                        <div class="prediction-box">

                            <div class="prediction-label">
                                Previsão do modelo
                            </div>

                            <div id="predictionValue">
                                --
                            </div>

                            <div id="predictionDescription">
                                --
                            </div>

                        </div>


                        <div class="risk-indicator">

                            <div class="risk-title">
                                Classificação
                            </div>

                            <div
                                id="riskCircle"
                                class="risk-circle"
                            >
                                --
                            </div>

                            <div id="riskText">
                                Aguardando análise
                            </div>

                        </div>


                    </div>


                    <div class="raw-section">

                        <div class="raw-title">
                            Resposta da API
                        </div>

                        <pre
                            id="resultContent"
                            class="raw-result"
                        ></pre>

                    </div>


                </div>

            </div>


        </div>

    </main>

</section>



<script>


/* =========================================================
   ELEMENTOS
========================================================= */

const loginPage =
    document.getElementById("loginPage");

const appPage =
    document.getElementById("appPage");

const loginForm =
    document.getElementById("loginForm");

const loginButton =
    document.getElementById("loginButton");

const loginError =
    document.getElementById("loginError");

const logoutButton =
    document.getElementById("logoutButton");

const predictionForm =
    document.getElementById("predictionForm");

const predictButton =
    document.getElementById("predictButton");

const resultCard =
    document.getElementById("resultCard");

const resultContent =
    document.getElementById("resultContent");

const predictionValue =
    document.getElementById("predictionValue");

const predictionDescription =
    document.getElementById(
        "predictionDescription"
    );

const loggedUser =
    document.getElementById(
        "loggedUser"
    );

const userAvatar =
    document.getElementById(
        "userAvatar"
    );

const riskCircle =
    document.getElementById(
        "riskCircle"
    );

const riskText =
    document.getElementById(
        "riskText"
    );


/* =========================================================
   EXIBIR APLICAÇÃO
========================================================= */

function showApplication(username) {

    loginPage.style.display = "none";

    appPage.classList.add("visible");

    const name =
        username || "Usuário";

    loggedUser.textContent =
        name;

    userAvatar.textContent =
        name
            .charAt(0)
            .toUpperCase();
}


/* =========================================================
   EXIBIR LOGIN
========================================================= */

function showLogin() {

    appPage.classList.remove(
        "visible"
    );

    loginPage.style.display =
        "flex";

    document
        .getElementById("password")
        .value = "";

    predictionForm.reset();

    resultCard.classList.remove(
        "visible"
    );
}


/* =========================================================
   LOGIN
========================================================= */

loginForm.addEventListener(
    "submit",
    async function(event) {

        event.preventDefault();

        loginError.classList.remove(
            "visible"
        );

        const username =
            document
                .getElementById(
                    "username"
                )
                .value;

        const password =
            document
                .getElementById(
                    "password"
                )
                .value;

        loginButton.disabled =
            true;

        loginButton.textContent =
            "Autenticando...";


        try {

            const response =
                await fetch(
                    "/auth/login",
                    {

                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify({
                                username:
                                    username,

                                password:
                                    password
                            }),

                        credentials:
                            "include"
                    }
                );


            const data =
                await response.json();


            if (!response.ok) {

                throw new Error(
                    data.detail ||
                    "Usuário ou senha inválidos."
                );
            }


            showApplication(
                data.username ||
                username
            );


        } catch (error) {

            loginError.textContent =
                error.message;

            loginError.classList.add(
                "visible"
            );

        } finally {

            loginButton.disabled =
                false;

            loginButton.textContent =
                "Entrar no sistema";
        }

    }
);


/* =========================================================
   LOGOUT
========================================================= */

logoutButton.addEventListener(
    "click",
    async function() {

        try {

            await fetch(
                "/auth/logout",
                {

                    method: "POST",

                    credentials:
                        "include"
                }
            );

        } finally {

            showLogin();
        }

    }
);


/* =========================================================
   RESULTADO VISUAL
========================================================= */

function updateRiskVisual(
    prediction
) {

    const normalized =
        String(prediction)
            .toLowerCase();


    const isChurn =
        normalized.includes("yes") ||
        normalized.includes("churn") ||
        normalized.includes("true") ||
        normalized === "1";


    if (isChurn) {

        predictionValue.style.color =
            "var(--danger)";

        riskCircle.style.color =
            "var(--danger)";

        riskCircle.style.background =
            "var(--danger-bg)";

        riskCircle.style.borderColor =
            "#fecaca";

        riskCircle.textContent =
            "ALTO";

        riskText.textContent =
            "Risco de cancelamento";

        predictionDescription.textContent =
            "O modelo identificou características associadas a um possível cancelamento deste cliente.";

    } else {

        predictionValue.style.color =
            "var(--success)";

        riskCircle.style.color =
            "var(--success)";

        riskCircle.style.background =
            "var(--success-bg)";

        riskCircle.style.borderColor =
            "#bbf7d0";

        riskCircle.textContent =
            "BAIXO";

        riskText.textContent =
            "Cliente com menor risco";

        predictionDescription.textContent =
            "O modelo não identificou características associadas a um risco elevado de cancelamento.";
    }

}


/* =========================================================
   PREDIÇÃO
========================================================= */

predictionForm.addEventListener(
    "submit",
    async function(event) {

        event.preventDefault();


        predictButton.disabled =
            true;

        predictButton.textContent =
            "Analisando cliente...";


        resultCard.classList.remove(
            "visible"
        );


        const data = {

            gender:
                document
                    .getElementById(
                        "gender"
                    )
                    .value,

            SeniorCitizen:
                Number(
                    document
                        .getElementById(
                            "SeniorCitizen"
                        )
                        .value
                ),

            Partner:
                document
                    .getElementById(
                        "Partner"
                    )
                    .value,

            Dependents:
                document
                    .getElementById(
                        "Dependents"
                    )
                    .value,

            tenure:
                Number(
                    document
                        .getElementById(
                            "tenure"
                        )
                        .value
                ),

            PhoneService:
                document
                    .getElementById(
                        "PhoneService"
                    )
                    .value,

            MultipleLines:
                document
                    .getElementById(
                        "MultipleLines"
                    )
                    .value,

            InternetService:
                document
                    .getElementById(
                        "InternetService"
                    )
                    .value,

            OnlineSecurity:
                document
                    .getElementById(
                        "OnlineSecurity"
                    )
                    .value,

            OnlineBackup:
                document
                    .getElementById(
                        "OnlineBackup"
                    )
                    .value,

            DeviceProtection:
                document
                    .getElementById(
                        "DeviceProtection"
                    )
                    .value,

            TechSupport:
                document
                    .getElementById(
                        "TechSupport"
                    )
                    .value,

            StreamingTV:
                document
                    .getElementById(
                        "StreamingTV"
                    )
                    .value,

            StreamingMovies:
                document
                    .getElementById(
                        "StreamingMovies"
                    )
                    .value,

            Contract:
                document
                    .getElementById(
                        "Contract"
                    )
                    .value,

            PaperlessBilling:
                document
                    .getElementById(
                        "PaperlessBilling"
                    )
                    .value,

            PaymentMethod:
                document
                    .getElementById(
                        "PaymentMethod"
                    )
                    .value,

            MonthlyCharges:
                Number(
                    document
                        .getElementById(
                            "MonthlyCharges"
                        )
                        .value
                ),

            TotalCharges:
                Number(
                    document
                        .getElementById(
                            "TotalCharges"
                        )
                        .value
                )
        };


        try {

            const response =
                await fetch(
                    "/predict",
                    {

                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        credentials:
                            "include",

                        body:
                            JSON.stringify(data)
                    }
                );


            if (
                response.status === 401
            ) {

                const errorData =
                    await response.json();

                showLogin();

                throw new Error(
                    errorData.detail ||
                    "Sessão inválida. Faça login novamente."
                );
            }


            const responseData =
                await response.json();


            if (!response.ok) {

                throw new Error(
                    responseData.detail ||
                    "Erro ao realizar previsão."
                );
            }


            resultContent.textContent =
                JSON.stringify(
                    responseData,
                    null,
                    4
                );


            let prediction = null;


            if (
                responseData.prediction !==
                undefined
            ) {

                prediction =
                    responseData.prediction;

            } else if (
                responseData.churn !==
                undefined
            ) {

                prediction =
                    responseData.churn;

            } else if (
                responseData.result !==
                undefined
            ) {

                prediction =
                    responseData.result;

            } else if (
                responseData.predicted_class !==
                undefined
            ) {

                prediction =
                    responseData.predicted_class;
            }


            if (
                prediction !== null
            ) {

                predictionValue.textContent =
                    String(prediction);

                updateRiskVisual(
                    prediction
                );

            } else {

                predictionValue.textContent =
                    "Concluído";

                predictionValue.style.color =
                    "var(--primary)";

                riskCircle.textContent =
                    "OK";

                riskText.textContent =
                    "Previsão processada";

                predictionDescription.textContent =
                    "A previsão foi processada com sucesso pelo modelo.";
            }


            resultCard.classList.add(
                "visible"
            );


            resultCard.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });


        } catch (error) {

            resultContent.textContent =
                "Erro: " +
                error.message;


            predictionValue.textContent =
                "Erro";

            predictionValue.style.color =
                "var(--danger)";


            riskCircle.textContent =
                "!";

            riskCircle.style.color =
                "var(--danger)";

            riskCircle.style.background =
                "var(--danger-bg)";

            riskCircle.style.borderColor =
                "#fecaca";


            riskText.textContent =
                "Falha na análise";


            predictionDescription.textContent =
                error.message;


            resultCard.classList.add(
                "visible"
            );

        } finally {

            predictButton.disabled =
                false;

            predictButton.textContent =
                "🔍 Analisar cliente";
        }

    }
);

</script>


</body>

</html>
"""


def get_home_page() -> HTMLResponse:
    """Retorna a interface web."""

    return HTMLResponse(
        content=HTML_PAGE
    )