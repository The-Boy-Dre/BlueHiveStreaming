// tools/anti_debug_snippets.js

(function() {
  // Use a safe way to log. If console.log is already overridden, this might not show.
  // We can create a custom log function just for this script for debugging its own execution.
  const _antiDebugLog = (message) => {
      // You could implement a more robust logger if needed, e.g., sending messages
      // to the Playwright script via page.exposeFunction or just rely on script errors.
      // For now, let's try to use the original console.log if possible,
      // or just accept that some logs might be suppressed by other overrides.
      try {
          // Check if console and console.log exist and if console.log appears to be native code
          if (window.console && typeof window.console.log === 'function' && Function.prototype.toString.call(window.console.log).includes('[native code]')) {
              window.console.log(`%c [Anti-Debug] ${message}`, 'color: #7FFF00; font-weight: bold;');
          }
      } catch (e) { /* ignore if console is too heavily restricted or doesn't exist */ }
  };

  _antiDebugLog('Snippets Injected!');

  // 1. Override specific 'debugger' function calls if known.
  // This is often more effective than trying to globally kill 'debugger;'.
  // Example: if a site has window.checkForDebugger = () => { debugger; };
  // window.checkForDebugger = () => { _antiDebugLog('checkForDebugger call bypassed.'); };
  // You'll need to identify these specific functions by stepping through code when it pauses.

  // 2. Subtler interference with timing-based debugger detection.
  // The idea is to make Date.now() and performance.now() slightly less predictable
  // or less "perfect" when DevTools are open, which might fool some checks.
  try {
      // Wrap Date.now
      if (typeof Date.now === 'function') {
          let lastDateNow = Date.now();
          const originalDateNow = Date.now;
          Date.now = function() {
              // Return the original value, but the act of overriding might break simple checks.
              // More aggressive: return originalDateNow() + Math.floor(Math.random() * 10);
              let now = originalDateNow.call(Date); // Ensure correct 'this' context
              if (now <= lastDateNow) { // Ensure time moves forward somewhat monotonically
                  now = lastDateNow + Math.floor(Math.random() * 5) + 1;
              }
              lastDateNow = now;
              return now;
          };
      } else {
          _antiDebugLog('Date.now function not found for wrapping.');
      }

      // Wrap performance.now - Check if 'performance' and 'performance.now' exist
      if (typeof window.performance === 'object' && typeof window.performance.now === 'function') {
          let lastPerfNow = window.performance.now();
          const originalPerfNow = window.performance.now;
          window.performance.now = function() {
              // Similar to Date.now
              let now = originalPerfNow.call(window.performance); // Ensure correct 'this'
              if (now <= lastPerfNow) {
                  now = lastPerfNow + (Math.random() * 5) + 0.001; // Add a small random increment
              }
              lastPerfNow = now;
              return now;
          };
          _antiDebugLog('Timing functions (Date.now, performance.now) have been wrapped.');
      } else {
          _antiDebugLog('window.performance or window.performance.now not found for wrapping.');
      }
  } catch (e) { _antiDebugLog(`Error wrapping timing functions: ${e.message || e}`); }

  // 3. Modify properties that indicate DevTools presence.
  // This is a common target.
  try {
      // For window.devtools property often checked
      const devtoolsPropertyDescriptor = {
          get: function() {
              _antiDebugLog('window.devtools.get intercepted, returning mock state.');
              return { isOpen: false, orientation: undefined, isDevtoolsDetecting: false }; // Always report closed & not detecting
          },
          set: function(val) {
              _antiDebugLog('Attempt to set window.devtools blocked.');
          },
          configurable: false, // Try to prevent site from redefining it
          enumerable: true, // Keep it enumerable if it was originally
      };

      if (window.hasOwnProperty('devtools')) { // Check if property exists to redefine
          Object.defineProperty(window, 'devtools', devtoolsPropertyDescriptor);
      } else {
          // If it doesn't exist, define it with the mock state
          Object.defineProperty(window, 'devtools', {
              ...devtoolsPropertyDescriptor,
              // If defining anew and 'get' is used, 'value' should not be present
              // Let's define it with a getter/setter consistently
          });
      }
      _antiDebugLog('window.devtools property has been managed.');
  } catch (e) { _antiDebugLog(`Error managing window.devtools property: ${e.message || e}`); }

  // 4. Handle the 'debugger' keyword by intercepting Function constructor (Use with caution)
  // This is aggressive and can break sites or be detected.
  // It tries to remove 'debugger;' statements from any dynamically generated functions.
  // It's often better to identify and override specific functions if possible.
  /*
  try {
      const originalFunction = Function;
      Function = function(...args) { // Use rest parameters
          const scriptBody = args[args.length - 1];
          if (typeof scriptBody === 'string' && scriptBody.includes('debugger')) {
              _antiDebugLog('Attempting to strip "debugger" from new Function source.');
              args[args.length - 1] = scriptBody.replace(/debugger;?/g, ';/* debugger removed *\/;');
          }
          return originalFunction.apply(this, args);
      };
      // Restore prototype and other static properties if necessary
      for (let key in originalFunction) {
          if (originalFunction.hasOwnProperty(key)) {
              Function[key] = originalFunction[key];
          }
      }
      Function.prototype = originalFunction.prototype;
      _antiDebugLog('Function constructor wrapped to remove "debugger".');
  } catch (e) { _antiDebugLog(`Error wrapping Function constructor: ${e.message || e}`); }
  */

  // 5. Prevent console.clear() (some scripts use this to hide their tracks or when devtools open)
  try {
      if (window.console && typeof window.console.clear === 'function') {
          window.console.clear = () => { _antiDebugLog('console.clear() call bypassed.'); };
      }
  } catch (e) { /* ignore */ }


  // 6. Override properties on navigator related to automation
  try {
      if (navigator.hasOwnProperty('webdriver')) {
          Object.defineProperty(navigator, 'webdriver', {
              get: () => {
                  _antiDebugLog('navigator.webdriver get intercepted, returning false.');
                  return false;
              },
              configurable: false, // Try to make it non-configurable
          });
      } else {
           // If it doesn't exist, define it as false
           Object.defineProperty(navigator, 'webdriver', {
              value: false,
              writable: false,
              configurable: false,
              enumerable: true,
          });
      }
      _antiDebugLog('navigator.webdriver property managed.');
  } catch (e) { _antiDebugLog(`Error managing navigator.webdriver: ${e.message || e}`); }

  // Example: If you find a specific function like `window.mySiteAntiDebugCheck()`
  // You could add:
  // if (typeof window.mySiteAntiDebugCheck === 'function') {
  //     window.mySiteAntiDebugCheck = () => {
  //         _antiDebugLog('mySiteAntiDebugCheck bypassed!');
  //         return false; // Or whatever it needs to return to allow normal operation
  //     };
  // }

  _antiDebugLog('Anti-Debug snippet execution finished.');
})();
