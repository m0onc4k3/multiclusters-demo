<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Sign in</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="${url.resourcesPath}/css/styles6.css" />
  <link rel="icon" type="image/x-icon" href="${url.resourcesPath}/img/favicon.ico" />
</head>
<body>
  <div class="login-container">
    <div class="logo-container">
      <img src="${url.resourcesPath}/img/logo.png" class="logo" alt="Logo">
    </div>
    <div class="header">
      <h2>Sign in</h2>
    </div>
    <form id="kc-form-login" action="${url.loginAction}" method="post">
      <div id="step1" class="step active">
        <div class="form-group">
          <!--
            <label for="username" class="sr-only">Email or Username</label>
          -->
          <input type="text" id="username" name="username" class="form-control" placeholder="Email or Username" autocomplete="off" required />
          <div id="username-error" class="error"></div>
        </div>
        <button type="button" class="btn btn-primary" id="nextStepBtn">Next</button>
      </div>
      <div id="step2" class="step">
        <div class="form-group">
          <!--
            <label for="password" class="sr-only">Password</label>
          -->
          <input type="password" id="password" name="password" class="form-control" placeholder="Password" autocomplete="current-password" required />
          <div id="password-error" class="error"></div>
        </div>
        <button type="submit" class="btn btn-primary">Login</button>
      </div>
    </form>
    <div class="footer">© 2025 NexaCorp. All rights reserved.</div>
  </div>
  <script src="${url.resourcesPath}/js/script6.js"></script>
</body>
</html>