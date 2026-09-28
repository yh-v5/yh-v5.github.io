// get the ninja-keys element
const ninja = document.querySelector('ninja-keys');

// add the home and posts menu items
ninja.data = [{
    id: "nav-about",
    title: "about",
    section: "Navigation",
    handler: () => {
      window.location.href = "/";
    },
  },{id: "nav-works",
          title: "works",
          description: "Selected works by Yeong Hwan Oh, with an exhibit page for each paper.",
          section: "Navigation",
          handler: () => {
            window.location.href = "/publications/";
          },
        },{id: "news-visited-the-calgary-ml-lab-prof-yani-ioannou-at-the-university-of-calgary-for-a-two-day-research-exchange-with-iris-lab",
          title: 'Visited the Calgary ML Lab (Prof. Yani Ioannou) at the University of Calgary...',
          description: "",
          section: "News",},{id: "news-our-paper-hyperspace-was-accepted-to-islped-2026",
          title: 'Our paper HyperSPACE was accepted to ISLPED 2026. 🎉',
          description: "",
          section: "News",},{id: "news-presented-hyperspace-at-islped-2026-in-evanston-il-the-paper-is-now-available-in-the-acm-digital-library",
          title: 'Presented HyperSPACE at ISLPED 2026 in Evanston, IL. The paper is now available...',
          description: "",
          section: "News",},{id: "news-our-paper-multi-centroid-hyperdimensional-computing-for-compact-imc-arrays-via-dimension-pruning-is-now-available-as-early-access-in-ieee-internet-of-things-journal",
          title: 'Our paper Multi-Centroid Hyperdimensional Computing for Compact IMC Arrays via Dimension Pruning is...',
          description: "",
          section: "News",},{id: "stories-your-resonance",
          title: 'Your Resonance',
          description: "A pilot adrift where one minute lasts nine days on Earth, and the one person who knows the rhythm of those tapping fingers.",
          section: "Stories",handler: () => {
              window.location.href = "/stories/neoui-ullim/";
            },},{id: "stories-be-right-back",
          title: 'Be Right Back',
          description: "Life is a game with no tutorial: a boy whose memories have no sound, and the neighbor who came from a world where the sun never sets.",
          section: "Stories",handler: () => {
              window.location.href = "/stories/danyeoolge/";
            },},{
      id: 'light-theme',
      title: 'Change theme to light',
      description: 'Change the theme of the site to Light',
      section: 'Theme',
      handler: () => {
        setThemeSetting("light");
      },
    },
    {
      id: 'dark-theme',
      title: 'Change theme to dark',
      description: 'Change the theme of the site to Dark',
      section: 'Theme',
      handler: () => {
        setThemeSetting("dark");
      },
    },
    {
      id: 'system-theme',
      title: 'Use system default theme',
      description: 'Change the theme of the site to System Default',
      section: 'Theme',
      handler: () => {
        setThemeSetting("system");
      },
    },];
