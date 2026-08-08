!macro NSIS_HOOK_PREUNINSTALL
  nsExec::ExecToStack 'taskkill /IM vuln-sentinel-desktop.exe /F /T'
  Pop $0
  nsExec::ExecToStack 'taskkill /IM vuln-sentinel-backend.exe /F /T'
  Pop $0
!macroend

!macro NSIS_HOOK_POSTUNINSTALL
  RMDir /r "$INSTDIR"
!macroend
