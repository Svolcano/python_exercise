// Copyright 2012 Google Inc. All rights reserved.
// Container Version: 1
(function(w, g) {
    w[g] = w[g] || {};
}
)(window, 'google_tag_manager');
(function() {

    /*
 jQuery v1.9.1 (c) 2005, 2012 jQuery Foundation, Inc. jquery.org/license. */
    var Gb = /\[object (Boolean|Number|String|Function|Array|Date|RegExp)\]/
      , Hb = function(a) {
        if (null == a)
            return String(a);
        var b = Gb.exec(Object.prototype.toString.call(Object(a)));
        return b ? b[1].toLowerCase() : "object"
    }
      , Ib = function(a, b) {
        return Object.prototype.hasOwnProperty.call(Object(a), b)
    }
      , La = function(a) {
        if (!a || "object" != Hb(a) || a.nodeType || a == a.window)
            return !1;
        try {
            if (a.constructor && !Ib(a, "constructor") && !Ib(a.constructor.prototype, "isPrototypeOf"))
                return !1
        } catch (c) {
            return !1
        }
        for (var b in a)
            ;
        return void 0 === b || Ib(a, b)
    }
      , V = function(a, b) {
        var c = b || ("array" == Hb(a) ? [] : {}), d;
        for (d in a)
            if (Ib(a, d)) {
                var e = a[d];
                "array" == Hb(e) ? ("array" != Hb(c[d]) && (c[d] = []),
                c[d] = V(e, c[d])) : La(e) ? (La(c[d]) || (c[d] = {}),
                c[d] = V(e, c[d])) : c[d] = e
            }
        return c
    };
    var Ha = {}
      , sb = null
      , Jb = Math.random();
    Ha.f = "GTM-WNMXQF";
    var Kb = null
      , Ca = null
      , jb = !1
      , Lb = "//www.googletagmanager.com/a?id=" + Ha.f + "&cv=1"
      , Mb = {}
      , Nb = {}
      , kb = {};
    var Ob, Pb, Qb, Rb, Sb, Tb, Ub, Vb, Wb, Xb, Yb, Zb, $b, ac, bc, cc, dc, ec, fc, gc, hc, ic, jc, kc, lc, mc, nc, oc, pc, qc, rc, sc, tc, uc, vc, wc, xc, yc, zc, Ac, Bc, Cc, Dc, Ec, Fc, Gc, Hc, Ic, Jc, Kc, Lc, Mc, Nc, Oc, Pc, Qc, Rc, Sc, Tc, Uc, Vc, Wc, Xc, Yc, Zc, $c, ad, bd, cd, dd, ed, fd, gd, hd, id, jd, kd, ld, md, nd, od, pd, qd, rd, sd, td, ud, vd, wd, xd, yd, Za, zd, Ad, Bd, Cd, Dd, Ed, Fd, Gd, Hd, Id, Jd, $a, Kd, Ld, Md, Nd, Od, Pd, Qd, Rd, Sd, Td, Ud, Vd, Wd, Xd, Yd, Zd, $d, ae, be, ce, de, ee, fe, ge, he, ie, je, ke, le, me, ne, oe, pe, qe, re, se, te, ue, ve, we, xe, ye, ze, Ae, Be, Ce, De, Ee, Fe, Ge, He, Ie, Je, Ke, Le, Me, Ne, Oe, Pe, Qe, Re, Se, Te, Ue, Ve, We, Xe, Ye, Ze, $e, af, bf, cf, df, ef, ff, gf, hf, jf, kf, lf, mf, nf, of, pf, qf, rf, sf, tf, uf, vf, wf, xf, yf, zf, Af, Bf, Cf, Df, Ef, Ff, Gf, Hf, If, Jf, Kf;
    (function() {
        var a = function(a) {
            return {
                toString: function() {
                    return a
                }
            }
        };
        Ob = a("");
        Pb = a("0");
        Qb = "";
        Rb = a("");
        Sb = a("");
        Tb = a("");
        Ub = a("");
        Vb = a("");
        Wb = a("");
        Xb = a("");
        Yb = a("");
        Zb = a("2");
        $b = a("3");
        ac = a("");
        bc = a("");
        cc = a("");
        dc = a("");
        ec = a("");
        fc = a("");
        gc = a("");
        hc = a("");
        ic = a("");
        jc = a("");
        kc = a("");
        lc = a("");
        mc = a("");
        nc = a("");
        oc = a("");
        pc = a("");
        qc = a("");
        rc = a("");
        sc = a("");
        tc = a("");
        uc = a("");
        vc = a("");
        wc = a("");
        xc = a("4");
        yc = a("");
        zc = a("");
        Ac = a("");
        Bc = a("");
        Cc = a("");
        Dc = a("");
        Ec = a("");
        Fc = a("");
        Gc = a("");
        Hc = a("");
        Ic = a("");
        Jc = a("");
        Kc = a("");
        Lc = a("");
        Mc = a("");
        Nc = a("");
        Oc = a("");
        Pc = a("");
        Qc = a("");
        Rc = a("5");
        Sc = a("");
        Tc = a("");
        Uc = a("6");
        Vc = a("");
        Wc = a("");
        Xc = a("");
        Yc = a("");
        Zc = a("");
        $c = a("");
        ad = a("");
        bd = a("");
        cd = a("7");
        dd = a("");
        ed = a("8");
        fd = a("");
        gd = a("");
        hd = a("");
        id = a("");
        jd = a("");
        kd = a("");
        ld = a("9");
        md = a("");
        nd = a("");
        od = a("");
        pd = a("");
        qd = a("");
        rd = a("");
        sd = a("");
        td = a("");
        ud = a("");
        vd = a("");
        wd = a("");
        xd = a("");
        yd = a("");
        Za = a("10");
        zd = a("");
        Ad = a("16");
        Bd = a("17");
        Cd = a("");
        Dd = a("");
        Ed = a("");
        Fd = a("");
        Gd = a("");
        Hd = a("");
        Id = a("");
        Jd = a("");
        $a = a("11");
        Kd = a("");
        Ld = a("");
        Md = a("");
        Nd = a("");
        Od = a("");
        Pd = a("");
        Qd = a("");
        Rd = a("");
        Sd = a("");
        Td = a("");
        Ud = a("12");
        Vd = a("");
        Wd = a("");
        Xd = a("");
        Yd = a("");
        Zd = a("");
        $d = a("");
        ae = a("");
        be = a("");
        ce = a("");
        de = a("");
        ee = a("");
        fe = a("");
        ge = a("");
        he = a("");
        ie = a("");
        je = a("");
        ke = a("");
        le = a("");
        me = a("");
        ne = a("");
        oe = a("");
        pe = a("");
        qe = a("");
        re = a("");
        se = a("");
        te = a("");
        ue = a("");
        ve = a("");
        we = a("");
        xe = a("");
        ye = a("");
        ze = a("");
        Ae = a("");
        Be = a("");
        Ce = a("");
        De = a("");
        Ee = a("");
        Fe = a("");
        Ge = a("");
        He = a("");
        Ie = a("");
        Je = a("");
        Ke = a("");
        Le = a("");
        Me = a("");
        Ne = a("");
        Oe = a("");
        Pe = a("");
        Qe = a("");
        Re = a("");
        Se = a("");
        Te = a("");
        Ue = a("");
        Ve = a("");
        We = a("");
        Xe = a("14");
        Ye = a("");
        Ze = a("");
        $e = a("");
        af = a("");
        bf = a("");
        cf = a("");
        df = a("");
        ef = a("");
        ff = a("");
        gf = a("");
        hf = a("");
        jf = a("");
        kf = a("");
        lf = a("");
        mf = a("");
        nf = a("");
        of = a("");
        pf = a("");
        qf = a("");
        rf = a("");
        sf = a("");
        tf = a("");
        uf = "";
        vf = a("");
        wf = a("");
        xf = a("");
        yf = a("");
        zf = a("");
        Af = a("15");
        Bf = a("");
        Cf = a("");
        Df = a("");
        Ef = a("");
        Ff = a("");
        Gf = a("");
        Hf = a("");
        If = a("");
        Jf = a("");
        Kf = a("")
    }
    )();
    var Fb = function(a, b) {
        V(a, b)
    }
      , Lf = function() {}
      , R = function(a) {
        return "function" == typeof a
    }
      , ab = function(a) {
        return "[object Array]" == Object.prototype.toString.call(Object(a))
    }
      , Mf = function(a) {
        return "number" == Hb(a) && !isNaN(a)
    }
      , Nf = function(a) {
        return /^[0-9]+$/.test(a)
    }
      , nb = function(a) {
        return "string" == Hb(a)
    }
      , Of = function(a, b) {
        if (Array.prototype.indexOf) {
            var c = a.indexOf(b);
            return "number" == typeof c ? c : -1
        }
        for (var d = 0; d < a.length; d++)
            if (a[d] === b)
                return d;
        return -1
    }
      , Pf = function(a, b) {
        if (a && ab(a) && 0 != a.length)
            for (var c = 0; c < a.length; c++)
                if (a[c] && b(a[c]))
                    return a[c]
    }
      , Ba = function(a) {
        return a ? a.replace(/^\s+|\s+$/g, "") : ""
    }
      , W = function(a) {
        return Math.round(Number(a)) || 0
    }
      , Oa = function(a) {
        return "false" == String(a).toLowerCase() ? !1 : !!a
    }
      , Qf = function(a) {
        var b = [];
        if (ab(a))
            for (var c = 0; c < a.length; c++)
                b.push(String(a[c]));
        return b
    }
      , Y = function() {
        return new Date
    }
      , Ga = function(a, b) {
        if (!Mf(a) || !Mf(b) || a > b)
            a = 0,
            b = 2147483647;
        return Math.floor(Math.random() * (b - a + 1) + a)
    }
      , Rf = function() {
        this.prefix = "gtm.";
        this.values = {}
    };
    Rf.prototype.set = function(a, b) {
        this.values[this.prefix + a] = b
    }
    ;
    Rf.prototype.get = function(a) {
        return this.values[this.prefix + a]
    }
    ;
    Rf.prototype.contains = function(a) {
        return void 0 !== this.get(a)
    }
    ;
    var Sf = function(a, b, c) {
        try {
            if (!a[Zd])
                return a[Za](a, b || Lf, c || Lf);
            c && c()
        } catch (d) {}
        return !1
    }
      , Tf = function(a, b) {
        function c(b, c) {
            a.contains(b) || a.set(b, []);
            a.get(b).push(c)
        }
        for (var d = Ba(b).split("&"), e = 0; e < d.length; e++)
            if (d[e]) {
                var f = d[e].indexOf("=");
                0 > f ? c(d[e], "1") : c(d[e].substring(0, f), d[e].substring(f + 1))
            }
    }
      , Uf = function(a) {
        var b = a ? a.length : 0;
        return 0 < b ? a[b - 1] : ""
    }
      , Vf = function(a) {
        var b = Ha.f;
        return function() {
            return a(b)
        }
    }
      , Wf = function(a) {
        for (var b = 0; b < a.length; b++)
            a[b]()
    }
      , Ka = function() {
        return "gtm" + Xf()
    }
      , Xf = function() {
        var a = sb.sequence || 0;
        sb.sequence = a + 1;
        return a
    }
      , Na = function(a, b, c) {
        return a && a.hasOwnProperty(b) ? a[b] : c
    }
      , Yf = function(a) {
        return null !== a && void 0 !== a && void 0 !== a.length
    }
      , Zf = function(a, b) {
        0 == b ? a.hc = !0 : a.ma = !0;
        var c = a.i;
        a.G && (a.G.yb[c] = b);
        Mb[c] && (Mb[c].state = b)
    }
      , $f = function(a, b) {
        return "function" != typeof String.prototype.startsWith ? 0 === a.indexOf(b) : a.startsWith(b)
    }
      , ag = function(a, b) {
        a.sort(function(a, d) {
            return b(a, d) ? -1 : b(d, a) ? 1 : 0
        })
    };
    var y = window
      , K = document
      , gg = navigator
      , hb = function(a, b) {
        var c = y[a];
        y[a] = void 0 === c ? b : c;
        return y[a]
    }
      , ib = function(a, b, c, d) {
        return (d || "http:" != y.location.protocol ? a : b) + c
    }
      , hg = function(a) {
        var b = K.getElementsByTagName("script")[0] || K.body || K.head;
        b.parentNode.insertBefore(a, b)
    }
      , ub = function(a, b) {
        b && (a.addEventListener ? a.onload = b : a.onreadystatechange = function() {
            a.readyState in {
                loaded: 1,
                complete: 1
            } && (a.onreadystatechange = null,
            b())
        }
        )
    }
      , u = function(a, b, c) {
        var d = K.createElement("script");
        d.type = "text/javascript";
        d.async = !0;
        d.src = a;
        ub(d, b);
        c && (d.onerror = c);
        hg(d);
        return d
    }
      , Xa = function(a, b) {
        var c = K.createElement("iframe");
        c.height = "0";
        c.width = "0";
        c.style.display = "none";
        c.style.visibility = "hidden";
        hg(c);
        ub(c, b);
        void 0 !== a && (c.src = a);
        return c
    }
      , G = function(a, b, c) {
        var d = new Image(1,1);
        d.onload = function() {
            d.onload = null;
            b && b()
        }
        ;
        d.onerror = function() {
            d.onerror = null;
            c && c()
        }
        ;
        d.src = a
    }
      , va = function(a, b, c, d) {
        a.addEventListener ? a.addEventListener(b, c, !!d) : a.attachEvent && a.attachEvent("on" + b, c)
    }
      , ra = function(a, b, c, d) {
        a.removeEventListener ? a.removeEventListener(b, c, !!d) : a.detachEvent && a.detachEvent("on" + b, c)
    }
      , w = function(a) {
        y.setTimeout(a, 0)
    }
      , ig = !1
      , jg = []
      , kg = function(a) {
        if (!ig) {
            var b = K.createEventObject
              , c = "complete" == K.readyState
              , d = "interactive" == K.readyState;
            if (!a || "readystatechange" != a.type || c || !b && d) {
                ig = !0;
                for (var e = 0; e < jg.length; e++)
                    w(jg[e])
            }
            jg.push = function() {
                for (var a = 0; a < arguments.length; a++)
                    w(arguments[a]);
                return 0
            }
        }
    }
      , lg = 0
      , mg = function() {
        if (!ig && 140 > lg) {
            lg++;
            try {
                K.documentElement.doScroll("left"),
                kg()
            } catch (a) {
                y.setTimeout(mg, 50)
            }
        }
    }
      , ha = function(a) {
        var b = K.getElementById(a);
        if (b && za(b, "id") != a)
            for (var c = 1; c < document.all[a].length; c++)
                if (za(document.all[a][c], "id") == a)
                    return document.all[a][c];
        return b
    }
      , za = function(a, b) {
        return a && b && a.attributes && a.attributes[b] ? a.attributes[b].value : null
    }
      , ng = function(a) {
        return a.target || a.srcElement || {}
    }
      , Aa = function(a) {
        var b = a.innerText || a.textContent || "";
        b && " " != b && (b = b.replace(/^[\s\xa0]+|[\s\xa0]+$/g, ""));
        b && (b = b.replace(/(\xa0+|\s{2,}|\n|\r\t)/g, " "));
        return b
    }
      , zb = function(a) {
        var b = K.createElement("div");
        b.innerHTML = "A<div>" + a + "</div>";
        b = b.lastChild;
        for (var c = []; b.firstChild; )
            c.push(b.removeChild(b.firstChild));
        return c
    }
      , og = function(a, b, c) {
        c = c || 100;
        for (var d = {}, e = 0; e < b.length; e++)
            d[b[e]] = !0;
        var f = a;
        for (e = 0; f && e <= c; e++) {
            if (d[String(f.tagName).toLowerCase()])
                return f;
            f = f.parentElement
        }
        return null
    }
      , pg = !1
      , qg = []
      , rg = function() {
        if (!pg) {
            pg = !0;
            for (var a = 0; a < qg.length; a++)
                w(qg[a])
        }
    }
      , sg = function(a) {
        a = a || y;
        var b = a.location.href
          , c = b.indexOf("#");
        return 0 > c ? "" : b.substring(c + 1)
    }
      , tb = function(a) {
        window.console && window.console.log && window.console.log(a)
    };
    var tg = function(a, b) {
        for (var c = a.split("&"), d = 0; d < c.length; d++) {
            var e = c[d].split("=");
            if (decodeURIComponent(e[0]).replace(/\+/g, " ") == b)
                return decodeURIComponent(e.slice(1).join("=")).replace(/\+/g, " ")
        }
    }
      , U = function(a, b, c, d, e) {
        var f, g = (a.protocol.replace(":", "") || y.location.protocol.replace(":", "")).toLowerCase();
        b && (b = String(b).toLowerCase());
        switch (b) {
        case "protocol":
            f = g;
            break;
        case "host":
            f = (a.hostname || y.location.hostname).split(":")[0].toLowerCase();
            if (c) {
                var h = /^www\d*\./.exec(f);
                h && h[0] && (f = f.substr(h[0].length))
            }
            break;
        case "port":
            f = String(1 * (a.hostname ? a.port : y.location.port) || ("http" == g ? 80 : "https" == g ? 443 : ""));
            break;
        case "path":
            f = "/" == a.pathname.substr(0, 1) ? a.pathname : "/" + a.pathname;
            var k = f.split("/");
            0 <= Of(d || [], k[k.length - 1]) && (k[k.length - 1] = "");
            f = k.join("/");
            break;
        case "query":
            f = a.search.replace("?", "");
            e && (f = tg(f, e));
            break;
        case "fragment":
            f = a.hash.replace("#", "");
            break;
        default:
            f = a && a.href
        }
        return f
    }
      , Da = function(a) {
        var b = "";
        if (a && a.href) {
            var c = a.href.indexOf("#");
            b = 0 > c ? a.href : a.href.substr(0, c)
        }
        return b
    }
      , T = function(a) {
        var b = K.createElement("a");
        a && (b.href = a);
        return b
    };
    var wa = function(a, b) {
        var c = function() {};
        c.prototype = a.prototype;
        var d = new c;
        a.apply(d, Array.prototype.slice.call(arguments, 1));
        return d
    };
    var ob = function(a) {
        return encodeURIComponent(a)
    }
      , ea = function(a) {
        var b = ["veinteractive.com", "ve-interactive.cn"];
        if (!a)
            return !1;
        var c = U(T(a), "host");
        if (!c)
            return !1;
        for (var d = 0; b && d < b.length; d++) {
            var e = b[d] && b[d].toLowerCase();
            if (e) {
                var f = c.length - e.length;
                0 < f && "." != e.charAt(0) && (f--,
                e = "." + e);
                if (0 <= f && c.indexOf(e, f) == f)
                    return !0
            }
        }
        return !1
    };
    var P = function(a, b, c) {
        for (var d = {}, e = !1, f = 0; a && f < a.length; f++)
            a[f] && a[f].hasOwnProperty(b) && a[f].hasOwnProperty(c) && (d[a[f][b]] = a[f][c],
            e = !0);
        return e ? d : null
    }
      , Ia = function(a, b) {
        V(a, b)
    }
      , Pa = function(a) {
        return W(a)
    }
      , Ab = function(a, b) {
        return Of(a, b)
    };
    /*
 Copyright (c) 2014 Derek Brans, MIT license https://github.com/krux/postscribe/blob/master/LICENSE. Portions derived from simplehtmlparser, which is licensed under the Apache License, Version 2.0 */
    var vg = {
        event: function(a) {
            var b = a[1];
            if (nb(b) && !(3 < a.length)) {
                var c;
                if (2 < a.length) {
                    if (!La(a[2]))
                        return;
                    c = a[2]
                }
                var d = c
                  , e = {
                    event: b
                };
                d && (d = V(d, void 0),
                e.eventModel = d,
                e.eventCallback = d.eventCallback);
                return e
            }
        },
        set: function(a) {
            var b;
            2 == a.length && La(a[1]) ? b = V(a[1], void 0) : 3 == a.length && nb(a[1]) && (b = {},
            b[a[1]] = a[2]);
            if (b)
                return b._clear = !0,
                b
        },
        js: function(a) {
            if (2 == a.length && a[1].getTime)
                return {
                    event: "gtm.js",
                    "gtm.start": a[1].getTime()
                }
        }
    };
    var wg = new Rf
      , xg = {}
      , zg = {
        set: function(a, b) {
            V(yg(a, b), xg)
        },
        get: function(a) {
            return Z(a, 2)
        },
        reset: function() {
            wg = new Rf;
            xg = {}
        }
    }
      , Z = function(a, b) {
        return 2 != b ? wg.get(a) : Ag(a)
    }
      , Ag = function(a) {
        for (var b = a.split("."), c = 0, d = xg.eventModel; void 0 !== d && c < b.length; c++) {
            if (null === d)
                return !1;
            d = d[b[c]]
        }
        if (void 0 !== d || 1 < c)
            return d;
        var e = xg;
        for (c = 0; c < b.length; c++) {
            if (null === e)
                return !1;
            if (void 0 === e[b[c]])
                return;
            e = e[b[c]]
        }
        return e
    }
      , Bg = function(a, b) {
        wg.set(a, b);
        V(yg(a, b), xg)
    }
      , yg = function(a, b) {
        for (var c = {}, d = c, e = a.split("."), f = 0; f < e.length - 1; f++)
            d = d[e[f]] = {};
        d[e[e.length - 1]] = b;
        return c
    };
    var Cg = !1
      , Dg = !1;
    var Eg = Math.random()
      , Fg = "0.050000" > Eg;
    var Gg = function(a, b) {
        if (Fg) {
            var c = Lb
              , d = function(a, b) {
                b && (c += a + encodeURIComponent(b))
            };
            d("&v=", "t");
            d("&n=", a);
            d("&s=", b && b.state);
            d("&h=", b && b.hideLatency);
            d("&g=", b && b.gaLatency);
            d("&p=", b && b.loadBy);
            d("&o=", b && b.timeout);
            d("&l=", Y().getTime() - W(Kb));
            c += "&sr=0.050000";
            d("&ps=", Eg);
            d("&cb=", Ga());
            G(c)
        }
    }
      , Hg = Lf
      , Ig = function() {
        var a = !1;
    };
    var Kg = function(a) {
        var b = sb.zones;
        return b ? b.checkState(Ha.f, a) : Jg
    }
      , qb = function(a) {
        var b = sb.zones;
        !b && a && (b = sb.zones = a());
        return b
    }
      , Jg = {
        active: !0,
        isWhitelisted: function() {
            return !0
        }
    };
    var Lg = Lf
      , Mg = []
      , Ng = !1
      , Og = function(a) {
        return y["dataLayer"].push(a)
    }
      , Pg = function(a) {
        var b = !1;
        return function() {
            !b && R(a) && w(Vf(a));
            b = !0
        }
    }
      , Yg = function() {
        for (var a = !1; !Ng && 0 < Mg.length; ) {
            Ng = !0;
            delete xg.eventModel;
            var b = Mg.shift();
            if (R(b))
                try {
                    b.call(zg)
                } catch (Ma) {}
            else if (ab(b))
                a: {
                    var c = b;
                    if (nb(c[0])) {
                        for (var d = c[0].split("."), e = d.pop(), f = c.slice(1), g = xg, h = 0; h < d.length; h++) {
                            if (void 0 === g[d[h]])
                                break a;
                            g = g[d[h]]
                        }
                        try {
                            g[e].apply(g, f)
                        } catch (Ma) {}
                    }
                }
            else {
                var k = b;
                if (k && ("[object Arguments]" == Object.prototype.toString.call(k) || Object.prototype.hasOwnProperty.call(k, "callee"))) {
                    a: {
                        var l = b;
                        if (l.length && nb(l[0])) {
                            var m = vg[l[0]];
                            if (m) {
                                b = m(l);
                                break a
                            }
                        }
                        b = void 0
                    }
                    if (!b) {
                        Ng = !1;
                        continue
                    }
                }
                var n = void 0
                  , p = void 0
                  , r = b
                  , t = r._clear;
                for (p in r)
                    r.hasOwnProperty(p) && "_clear" !== p && (t && Bg(p, void 0),
                    Bg(p, r[p]));
                var v = !1
                  , z = r.event;
                if (z) {
                    r.hasOwnProperty("gtm.uniqueEventId") || (r["gtm.uniqueEventId"] = Xf(),
                    Bg("gtm.uniqueEventId", r["gtm.uniqueEventId"]));
                    n = r["gtm.uniqueEventId"];
                    Ca = z;
                    var J = Kg(n);
                    if (J.active) {
                        var F = Pg(r.eventCallback)
                          , E = r.eventTimeout;
                        E && y.setTimeout(F, Number(E));
                        v = Lg(n, z, J.isWhitelisted, F, r.eventReporter)
                    }
                }
                Kb || (Kb = r["gtm.start"]) && Hg();
                var L, B = r, D = n, A = z, C = xg;
                Ca = null;
                a = v || a
            }
            Ng = !1
        }
        return !a
    }
      , Zg = function() {
        var a = Yg();
        try {
            var b = y["dataLayer"].hide;
            if (b && void 0 !== b[Ha.f] && b.end) {
                b[Ha.f] = !1;
                var c = !0, d;
                for (d in b)
                    if (b.hasOwnProperty(d) && !0 === b[d]) {
                        c = !1;
                        break
                    }
                c && (b.end(),
                b.end = null)
            }
        } catch (e) {}
        return a
    }
      , $g = function() {
        var a = hb("dataLayer", [])
          , b = hb("google_tag_manager", {});
        b = b["dataLayer"] = b["dataLayer"] || {};
        jg.push(function() {
            b.gtmDom || (b.gtmDom = !0,
            a.push({
                event: "gtm.dom"
            }))
        });
        qg.push(function() {
            b.gtmLoad || (b.gtmLoad = !0,
            a.push({
                event: "gtm.load"
            }))
        });
        var c = a.push;
        a.push = function() {
            var b = [].slice.call(arguments, 0);
            c.apply(a, b);
            for (Mg.push.apply(Mg, b); 300 < this.length; )
                this.shift();
            return Yg()
        }
        ;
        Mg.push.apply(Mg, a.slice(0));
        w(Zg)
    };
    var ah, bh, ch;
    var Ea = function(a, b) {
        var c = {
            "gtm.element": a,
            "gtm.elementClasses": a.className,
            "gtm.elementId": a["for"] || za(a, "id") || "",
            "gtm.elementTarget": a.formTarget || a.target || ""
        };
        if (b && eh)
            if ("LINK_CLICK" == b)
                c["gtm.elementUrl"] = a.href;
            else if ("FORM_SUBMIT" == b) {
                var d = a.action;
                d && d.tagName && (d = a.cloneNode(!1).action);
                c["gtm.elementUrl"] = d
            }
        c.hasOwnProperty("gtm.elementUrl") || (c["gtm.elementUrl"] = (a.attributes && a.attributes.formaction ? a.formAction : "") || a.action || a.href || a.src || a.code || a.codebase || "");
        return c
    }
      , th = function(a) {
        sb.hasOwnProperty("autoEventsSettings") || (sb.autoEventsSettings = {});
        var b = sb.autoEventsSettings;
        b.hasOwnProperty(a) || (b[a] = {});
        return b[a]
    }
      , pa = function(a, b, c) {
        th(a)[b] = c
    }
      , gb = function(a, b, c, d) {
        var e = th(a)
          , f = Na(e, b, d);
        e[b] = c(f)
    }
      , ta = function(a, b, c) {
        var d = th(a);
        return Na(d, b, c)
    }
      , qa = function(a) {
        return !!ta(a, "init", !1)
    }
      , ua = function(a) {
        pa(a, "init", !0)
    }
      , uh = function() {};
    var vh = /(^|\.)doubleclick\.net$/i
      , wh = /^(www\.)?google(\.com?)?(\.[a-z]{2})?$/
      , Fa = function(a, b, c) {
        for (var d = String(b || K.cookie).split(";"), e = [], f = 0; f < d.length; f++) {
            var g = d[f].split("=")
              , h = Ba(g[0]);
            if (h && h == a) {
                var k = Ba(g.slice(1).join("="));
                k && !1 !== c && (k = decodeURIComponent(k));
                e.push(k)
            }
        }
        return e
    }
      , yh = function(a, b, c, d, e, f) {
        f && (b = encodeURIComponent(b));
        var g = a + "=" + b + "; ";
        c && (g += "path=" + c + "; ");
        e && (g += "expires=" + e.toGMTString() + "; ");
        var h;
        h = "auto" == d ? xh() : [d || "none"];
        for (var k = 0; k < h.length; k++) {
            var l = g
              , m = h[k]
              , n = c;
            if (vh.test(y.location.hostname) || "/" == n && wh.test(m))
                break;
            "none" != h[k] && (l += "domain=" + h[k] + ";");
            var p = K.cookie;
            K.cookie = l;
            if (p != K.cookie || 0 <= Of(Fa(a), b))
                return !0
        }
        return !1
    }
      , zh = function(a) {
        if ("none" == a)
            return 0;
        0 == a.indexOf(".") && (a = a.substr(1));
        return a.split(".").length
    }
      , Ah = function(a) {
        var b = a;
        b ? (1 < b.length && b.lastIndexOf("/") == b.length - 1 && (b = b.substr(0, b.length - 1)),
        0 != b.indexOf("/") && (b = "/" + b),
        a = b) : a = "/";
        return "/" == a ? 1 : a.split("/").length
    }
      , xh = function() {
        var a = U(y.location, "host", !0).split(".");
        if (4 == a.length && /^[0-9]*$/.exec(a[3]))
            return ["none"];
        for (var b = [], c = a.length - 2; 0 <= c; c--)
            b.push(a.slice(c).join("."));
        b.push("none");
        return b
    };
    var fa = function(a) {
        var b = K;
        return Bh ? b.querySelectorAll(a) : null
    }
      , Ch = !1;
    if (K.querySelectorAll)
        try {
            var Dh = K.querySelectorAll(":root");
            Dh && 1 == Dh.length && Dh[0] == K.documentElement && (Ch = !0)
        } catch (a) {}
    var Bh = Ch;
    var Eh = function(a) {
        for (var b = [], c = K.cookie.split(";"), d = new RegExp("^\\s*" + a + "=\\s*(.*?)\\s*$"), e = 0; e < c.length; e++) {
            var f = c[e].match(d);
            f && b.push(f[1])
        }
        var g = [];
        if (!b || 0 == b.length)
            return g;
        for (var h = 0; h < b.length; h++) {
            var k = b[h].split(".");
            3 == k.length && "GCL" == k[0] && k[1] && g.push(k[2])
        }
        return g
    };
    var Fh = /^\w+$/
      , Gh = /^[\w-]+$/
      , Hh = /^\d+\.fls\.doubleclick\.net$/;
    function Ih(a) {
        return a && "string" == typeof a && a.match(Fh) ? a : "_gcl"
    }
    function Jh(a) {
        if (a) {
            if ("string" == typeof a) {
                var b = Ih(a);
                return {
                    na: b,
                    la: b
                }
            }
            if (a && "object" == typeof a)
                return {
                    na: Ih(a.dc),
                    la: Ih(a.aw)
                }
        }
        return {
            na: "_gcl",
            la: "_gcl"
        }
    }
    function Kh(a) {
        var b = T(y.location.href)
          , c = U(b, "host", !1);
        if (c && c.match(Hh)) {
            var d = U(b, "path").split(a + "=");
            if (1 < d.length)
                return d[1].split(";")[0].split("?")[0]
        }
    }
    function Lh(a) {
        return a.filter(function(a) {
            return Gh.test(a)
        })
    }
    var Nh = function(a) {
        var b = Kh("gclaw");
        if (b)
            return b.split(".");
        var c = Jh(a);
        if ("_gcl" == c.la) {
            var d = Mh();
            if (d && (null == d.L || "aw.ds" == d.L))
                return [d.qa]
        }
        return Lh(Eh(c.la + "_aw"))
    }
      , Oh = function(a) {
        var b = Kh("gcldc");
        if (b)
            return b.split(".");
        var c = Jh(a);
        if ("_gcl" == c.na) {
            var d = Mh();
            if (d && ("ds" == d.L || "aw.ds" == d.L))
                return [d.qa]
        }
        return Lh(Eh(c.na + "_dc"))
    };
    function Mh() {
        var a = T(y.location.href)
          , b = U(a, "query", !1, void 0, "gclid")
          , c = U(a, "query", !1, void 0, "gclsrc");
        if (!b || !c) {
            var d = U(a, "fragment");
            b = b || tg(d, "gclid");
            c = c || tg(d, "gclsrc")
        }
        return void 0 !== b && b.match(Gh) ? {
            qa: b,
            L: c
        } : null
    }
    var Ya = function(a, b, c) {
        var d = Jh(a);
        c = c || "auto";
        b = b || "/";
        var e = Mh();
        if (null !== e) {
            var f = (new Date).getTime()
              , g = new Date(f + 7776E6)
              , h = ["GCL", Math.round(f / 1E3), e.qa].join(".");
            e.L && "aw.ds" != e.L || yh(d.la + "_aw", h, b, c, g, !0);
            "aw.ds" != e.L && "ds" != e.L || yh(d.na + "_dc", h, b, c, g, !0)
        }
    }
      , Ph = function() {
        var a = Kh("gac");
        if (a)
            return decodeURIComponent(a);
        for (var b = [], c = K.cookie.split(";"), d = /^\s*_gac_(UA-\d+-\d+)=\s*(.+?)\s*$/, e = 0; e < c.length; e++) {
            var f = c[e].match(d);
            f && b.push({
                Ab: f[1],
                value: f[2]
            })
        }
        var g = {};
        if (b && b.length)
            for (var h = 0; h < b.length; h++) {
                var k = b[h].value.split(".");
                "1" == k[0] && 3 == k.length && k[1] && (g[b[h].Ab] || (g[b[h].Ab] = []),
                g[b[h].Ab].push({
                    timestamp: k[1],
                    qa: k[2]
                }))
            }
        var l = [], m;
        for (m in g)
            if (g.hasOwnProperty(m)) {
                for (var n = [], p = g[m], r = 0; r < p.length; r++)
                    n.push(p[r].qa);
                n = Lh(n);
                n.length && l.push(m + ":" + n.join(","))
            }
        return l.join(";")
    };
    var Qh;
    a: {
        Qh = "G"
    }
    var Rh = {
        "": "n",
        UA: "u",
        AW: "a",
        DC: "d",
        GTM: Qh
    }
      , ya = function(a) {
        var b = Ha.f.split("-")
          , c = b[0].toUpperCase();
        return (Rh[c] || "i") + "32" + (a && "GTM" === c ? b[1] : "")
    };
    var lb = new String("undefined")
      , Vh = function(a) {
        this.resolve = function(b) {
            for (var c = [], d = 0; d < a.length; d++)
                c.push(a[d] === lb ? b : a[d]);
            return c.join("")
        }
    };
    Vh.prototype.toString = function() {
        return this.resolve("undefined")
    }
    ;
    Vh.prototype.valueOf = Vh.prototype.toString;
    var Wh = {}
      , Xh = function(a, b) {
        var c = Xf();
        Wh[c] = [a, b];
        return c
    }
      , Yh = function(a) {
        var b = a ? 0 : 1;
        return function(a) {
            var c = Wh[a];
            if (c && R(c[b]))
                c[b]();
            Wh[a] = void 0
        }
    };
    var Zh = {}, $h, ai;
    var ji = function() {};
    var bb = function(a, b, c, d) {
        va(a, b, c, d)
    }
      , ka = function(a, b) {
        return y.setTimeout(a, b)
    }
      , ba = function(a, b, c) {
        u(a, b, c)
    }
      , db = {}
      , Sa = function(a, b, c) {
        var d = db[a];
        if (void 0 === d) {
            var e = function(a, b) {
                return function() {
                    a.status = b;
                    for (var c = 2 == b ? a.wb : a.cb, d = 0; d < c.length; d++)
                        y.setTimeout(c[d], 0)
                }
            };
            d = {
                status: 1,
                wb: [],
                cb: [],
                ec: void 0
            };
            d.qd = u(a, e(d, 2), e(d, 3));
            db[a] = d
        }
        0 === d.status && (d.ec(),
        d.status = 2);
        2 === d.status ? b && b() : 3 === d.status ? c && c() : 1 === d.status && (b && d.wb.push(b),
        c && d.cb.push(c))
    }
      , ri = function(a, b) {
        db[a] = {
            status: 0,
            wb: [],
            cb: [],
            ec: b,
            qd: null
        }
    }
      , ca = function() {
        return y.location.href
    }
      , cb = function(a) {
        return U(T(a), "fragment")
    }
      , S = function(a, b) {
        return Z(a, b || 2)
    }
      , na = function(a, b, c) {
        b && (a.eventCallback = b,
        c && (a.eventTimeout = c));
        return Og(a)
    }
      , aa = function(a, b) {
        y[a] = b
    }
      , q = function(a, b, c) {
        var d = y;
        b && (void 0 === d[a] || c && !d[a]) && (d[a] = b);
        return d[a]
    }
      , eb = function(a, b) {
        return og(a, b, 100)
    }
      , x = function(a, b, c, d) {
        var e = !d && "http:" == y.location.protocol;
        e && (e = 2 !== pb());
        return (e ? b : a) + c
    }
      , vb = function(a) {
        ig ? a() : jg.push(a)
    };
    var ia = function(a) {
        var b = 0;
        return b
    }
      , Cb = function(a) {}
      , ja = function(a) {
        var b = !1;
        return b
    }
      , fb = function(a, b) {
        return Pf(a, b)
    }
      , oa = function(a, b, c, d) {
        gb(a, b, c, d)
    }
      , sa = function(a, b, c) {
        return ta(a, b, c)
    };
    var Eb = void 0
      , Va = function(a) {
        if (!Eb) {
            var b = function() {
                var a = K.body;
                if (a)
                    if (q("MutationObserver"))
                        (new MutationObserver(function() {
                            for (var a = 0; a < Eb.length; a++)
                                w(Eb[a])
                        }
                        )).observe(a, {
                            childList: !0,
                            subtree: !0
                        });
                    else {
                        var b = !1;
                        bb(a, "DOMNodeInserted", function() {
                            b || (b = !0,
                            w(function() {
                                b = !1;
                                for (var a = 0; a < Eb.length; a++)
                                    w(Eb[a])
                            }))
                        })
                    }
            };
            Eb = [];
            K.body ? b() : w(b)
        }
        Eb.push(a)
    }
      , pb = function() {
        var a;
        a = "www.googletagmanager.com/gtm.js";
        for (var b = "https://" + a, c = "http://" + a, d = 1, e = K.getElementsByTagName("script"), f = 0; f < e.length && 100 > f; f++) {
            var g = e[f].src;
            if (g) {
                g = g.toLowerCase();
                if ($f(g, c))
                    return 3;
                1 === d && $f(g, b) && (d = 2)
            }
        }
        return d
    };
    var rb = function(a) {
        var b = "www.googletagmanager.com/gtm.js?id=" + encodeURIComponent(a) + "&l=dataLayer";
        u(x("https://", "http://", b), void 0, void 0)
    };
    var xb = function(a, b, c) {
        a instanceof Vh && (a = a.resolve(Xh(b, c)),
        b = Lf);
        return {
            hb: a,
            w: b
        }
    };
    var si = new RegExp(/^(.*\.)?(google|youtube|blogger|withgoogle)(\.com?)?(\.[a-z]{2})?\.?$/)
      , ti = {
        customPixels: ["nonGooglePixels"],
        html: ["customScripts", "customPixels", "nonGooglePixels", "nonGoogleScripts", "nonGoogleIframes"],
        customScripts: ["html", "customPixels", "nonGooglePixels", "nonGoogleScripts", "nonGoogleIframes"],
        nonGooglePixels: [],
        nonGoogleScripts: ["nonGooglePixels"],
        nonGoogleIframes: ["nonGooglePixels"]
    }
      , ui = {
        customPixels: ["customScripts", "html"],
        html: ["customScripts"],
        customScripts: ["html"],
        nonGooglePixels: ["customPixels", "customScripts", "html", "nonGoogleScripts", "nonGoogleIframes"],
        nonGoogleScripts: ["customScripts", "html"],
        nonGoogleIframes: ["customScripts", "html", "nonGoogleScripts"]
    }
      , vi = function(a, b) {
        for (var c = [], d = 0; d < a.length; d++)
            c.push(a[d]),
            c.push.apply(c, b[a[d]] || []);
        return c
    }
      , Rg = function(a) {
        var b = Z("gtm.whitelist");
        var c = b && vi(Qf(b), ti)
          , d = Z("gtm.blacklist") || Z("tagTypeBlacklist") || [];
        si.test(y.location && y.location.hostname) && (d = Qf(d),
        d.push("nonGooglePixels", "nonGoogleScripts"));
        var e = d && vi(Qf(d), ui)
          , f = {};
        return function(g) {
            var h = g && g[Za];
            if (!h)
                return !0;
            if (void 0 !== f[h.a])
                return f[h.a];
            var k = a(h.a);
            if (b) {
                var l;
                if (l = k)
                    a: {
                        if (0 > Of(c, h.a))
                            if (h.b && 0 < h.b.length)
                                for (var m = 0; m < h.b.length; m++) {
                                    if (0 > Of(c, h.b[m])) {
                                        l = !1;
                                        break a
                                    }
                                }
                            else {
                                l = !1;
                                break a
                            }
                        l = !0
                    }
                k = l
            }
            var n = !1;
            if (d) {
                var p;
                if (!(p = 0 <= Of(e, h.a)))
                    a: {
                        for (var r = h.b || [], t = new Rf, v = 0; v < e.length; v++)
                            t.set(e[v], !0);
                        for (v = 0; v < r.length; v++)
                            if (t.get(r[v])) {
                                p = !0;
                                break a
                            }
                        p = !1
                    }
                n = p
            }
            return f[h.a] = !k || n
        }
    };
    var _eu = function(a) {
        var b = String(Z("gtm.elementUrl") || a[Xc] || "")
          , c = T(b);
        return b
    };
    _eu.a = "eu";
    _eu.b = ["google"];
    var _e = function() {
        return Ca
    };
    _e.a = "e";
    _e.b = ["google"];
    var Ai = function(a, b) {
        this.h = a;
        this.s = b
    };
    Ai.prototype.toString = function() {
        var a = "" + this.h;
        1 < this.s && (a = a + "-" + this.s);
        return a
    }
    ;
    var Bi = function(a, b) {
        this.vb = a;
        this.Ma = b
    };
    Bi.prototype.toString = function() {
        return "" + this.Ma + "." + this.vb
    }
    ;
    var Ei = function(a, b) {
        var c = new Ci(null,a,b);
        Di(c);
        return c
    }
      , Ci = function(a, b, c) {
        this.Pb = Math.floor(Y().getTime() / 864E5);
        this.Ka = b || "auto";
        this.ua = c || "/";
        var d = zh(this.Ka)
          , e = Ah(this.ua);
        this.N = a || new Ai(d,e);
        this.m = [];
        this.I = new Rf
    }
      , Gi = function(a, b, c) {
        b && ("" == c.vb ? Fi(a, b) : (a.I.contains(b) || a.m.push(b),
        a.I.set(b, c)))
    }
      , Hi = function(a, b) {
        for (var c = 0; c < b.length; c++)
            Gi(a, b[c][0], b[c][1])
    }
      , Fi = function(a, b) {
        var c = Of(a.m, b);
        0 <= c && a.m.splice(c, 1);
        a.I.set(b, void 0)
    }
      , Ii = function(a) {
        for (var b = [], c = 0; c < a.m.length; c++) {
            var d = a.m[c];
            b.push([d, a.I.get(d)])
        }
        return b
    }
      , Ji = function(a) {
        for (var b = 0, c = 0; c < a.m.length; c++)
            b = Math.max(b, a.I.get(a.m[c]).Ma);
        return 864E5 * b
    };
    Ci.prototype.toString = function() {
        if (0 == this.m.length)
            return "";
        for (var a = [], b = 0; b < this.m.length; b++) {
            var c = this.m[b];
            a.push("" + c + "." + this.I.get(c).toString())
        }
        return "GAX1." + this.N.toString() + "." + a.join("!")
    }
    ;
    var Ki = function(a, b) {
        for (var c = new Date, d = Ah(a.ua), e = [], f = 0; f < a.m.length; f++) {
            var g = a.m[f];
            a.I.get(g).Ma < a.Pb && e.push(g)
        }
        for (f = 0; f < e.length; f++)
            Fi(a, e[f]);
        if (a.m.length > (b || 10))
            return !1;
        c.setTime(Ji(a));
        if ("auto" != a.Ka)
            return yh("_gaexp", a.toString(), a.ua, a.Ka, c);
        for (var h = xh(), k = 0; k < h.length; k++)
            if ("none" != h[k] && (a.N = new Ai(zh(h[k]),d),
            yh("_gaexp", a.toString(), a.ua, h[k], c)))
                return !0;
        return !1
    }
      , Di = function(a) {
        for (var b = a.N.h, c = a.N.s, d = Fa("_gaexp"), e = [], f = 0; f < d.length; f++) {
            var g = Li(a, d[f]);
            g && e.push(g)
        }
        ag(e, function(a, d) {
            var e = a.N
              , f = d.N;
            return e.h == f.h && e.s == f.s ? !1 : e.h == b && e.s == c ? !0 : f.h == b && f.s == c ? !1 : e.h == b ? f.h != b || e.s < f.s : f.h == b ? !1 : e.s == c ? f.h != b && (f.s != c || e.h < f.h) : f.s == c ? !1 : e.h < f.h || e.h == f.h && e.s < f.s
        });
        a.N = 0 < e.length ? e[0].N : new Ai(b,c);
        for (f = e.length - 1; 0 <= f; f--)
            Hi(a, Ii(e[f]))
    }
      , Li = function(a, b) {
        var c = b.match(/GAX1\.([^.]+).(.*)/);
        if (c) {
            var d;
            a: {
                var e = (c[1] || "").split("-");
                if (!(0 == e.length || 2 < e.length)) {
                    var f = Ba(e[0]);
                    if (0 != f.length) {
                        var g = 2 == e.length ? Ba(e[1]) : "1";
                        if (Nf(f) && Nf(g)) {
                            d = new Ai(W(f),W(g));
                            break a
                        }
                    }
                }
                d = void 0
            }
            if (d) {
                for (var h = new Ci(d,a.Ka,a.ua), k = (c[2] || "").split("!"), l = 0; l < k.length; l++) {
                    var m = k[l].split(".");
                    if (3 == m.length) {
                        if (!Nf(m[1]))
                            return;
                        Gi(h, m[0], new Bi(m[2],W(m[1])))
                    }
                }
                return h
            }
        }
    };
    var _f = function(a) {
        var b = String(Z("gtm.referrer") || K.referrer);
        if (!b)
            return b;
        var c = T(b);
        return b
    };
    _f.a = "f";
    _f.b = ["google"];
    var Pi = function(a) {
        var b = y.location, c;
        (c = a[Mc] ? a[Mc] : Z("gtm.url")) && (b = T(String(c)));
        var d = b.href
          , e = d.indexOf("#")
          , f = 0 > e ? d : d.substr(0, e);
        a[xc] && (f = U(b, a[xc], a[Re], a[Wc], a[Ee]));
        return f
    }
      , _u = Pi;
    _u.a = "u";
    _u.b = ["google"];
    var _eq = function(a) {
        return String(a[Zb]) == String(a[$b])
    };
    _eq.a = "eq";
    _eq.b = ["google"];
    var mj = function(a, b, c, d, e) {
        var f = a + "{" + (b + ": " + c + (d ? " !important" : "")) + "}";
        e && (f = e + "{" + f + "}");
        var g = document;
        if (g.createStyleSheet) {
            var h = jj(g)
              , k = h.rules.length;
            h.insertRule(f, k);
            return function() {
                h.deleteRule ? h.deleteRule(k) : h.removeRule(k);
                h.insertRule("x {}", k)
            }
        }
        var l = kj(f, g);
        lj(l, g);
        var m = l.parentNode;
        return function() {
            m.removeChild(l)
        }
    }
      , nj = null
      , jj = function(a) {
        if (nj)
            return nj;
        for (var b = a.styleSheets.length - 1; 0 <= b; b--) {
            var c = a.styleSheets[b]
              , d = c.ownerNode;
            if (d && d.parentNode && "HEAD" == d.parentNode.tagName)
                return nj = c
        }
        0 == a.styleSheets.length && a.createStyleSheet();
        return nj = a.styleSheets[0]
    }
      , kj = function(a, b) {
        var c = (b || document).createElement("style");
        void 0 !== c.cssText ? c.cssText = a : c.innerHTML = a;
        return c
    }
      , lj = function(a, b) {
        var c = b || document
          , d = c.getElementsByTagName("head")[0];
        d || (d = c.createElement("head"),
        c.body.parentNode.insertBefore(d, c.body));
        d.appendChild(a)
    };
    var uj = {}
      , vj = void 0
      , wj = function(a) {
        var b = uj[a];
        b || (b = {
            id: a,
            A: [],
            pa: 0,
            Bb: null,
            kb: void 0,
            qb: !1
        },
        uj[a] = b);
        vj = b
    }
      , yj = function(a, b, c, d) {
        var e = vj;
        if (!Bh || !e)
            return !1;
        var f = {
            id: e.id + ":" + e.A.length,
            vc: b,
            fa: [],
            qc: c,
            O: a,
            Za: 0,
            Ua: d || null,
            Ob: 0,
            oa: !1
        };
        e.A.push(f);
        null === a ? (f.oa = !0,
        b(null)) : xj(e);
        return !0
    }
      , zj = function(a) {
        var b = mj(a, "visibility", "hidden", !0);
        return function() {
            R(b) && b.apply();
            b = null
        }
    }
      , Aj = function(a, b, c, d) {
        var e = b;
        if (!ig) {
            var f = zj(a.F);
            jg.push(f);
            e = function(a, c) {
                var d = b(a, c);
                f();
                return d
            }
        }
        return yj(a, e, c, d)
    }
      , xj = function(a) {
        if (!a.qb) {
            for (var b = a.pa; b < a.A.length; b++) {
                var c = a.A[b]
                  , d = b == a.pa;
                if (!c.oa && !Bj(d, c))
                    break;
                c.oa && d && a.pa++
            }
            a.A.length > a.pa ? (a.Bb || (a.Bb = y.setTimeout(function() {
                a.Bb = null;
                xj(a)
            }, 80)),
            ig || a.kb || (a.kb = function() {
                w(function() {
                    xj(a)
                })
            }
            ,
            va(K, "DOMContentLoaded", a.kb))) : Cj(a)
        }
    }
      , Cj = function(a) {
        for (var b = 0; b < a.A.length; b++) {
            var c = a.A[b];
            if (c.O)
                for (var d = fa(c.O.F) || [], e = 0; e < d.length; e++) {
                    var f = d[e];
                    f.gtmProgressiveApplied && f.gtmProgressiveApplied[c.id] || (Dj(f, c.id),
                    c.fa.push(Ej(f, c.id)))
                }
        }
    }
      , Bj = function(a, b) {
        var c = [];
        if (b.O) {
            var d = Fj(b.O, b.id)
              , e = null;
            b.Ua && (e = Fj(b.Ua, b.id + "-t"));
            for (var f = 0; f < d.length; f++) {
                var g = d[f], h;
                if (null != e && (h = e.length > f ? e[f] : null,
                !h && !ig && (null === b.Ua.v || b.Ob + c.length < b.Ua.v)))
                    break;
                c.push({
                    element: g,
                    td: h
                })
            }
        }
        if (!ig && b.qc && (!a || null == b.O.v || b.O.v != b.Za + c.length))
            return !1;
        for (var k = 0; k < c.length; k++) {
            var l = c[k].element, m = c[k].td, n;
            b.Za++;
            Dj(l, b.id);
            m && (b.Ob++,
            n = b.id + "-t",
            Dj(m, n));
            var p = b.vc(l, m);
            R(p) && b.fa.push(p);
            b.fa.push(Ej(l, b.id));
            m && n && b.fa.push(Ej(m, n))
        }
        if (b.O.v && b.O.v == b.Za || ig)
            b.oa = !0;
        return !0
    }
      , Dj = function(a, b) {
        a.gtmProgressiveApplied || (a.gtmProgressiveApplied = {});
        a.gtmProgressiveApplied[b] = !0
    }
      , Ej = function(a, b) {
        return function() {
            a.gtmProgressiveApplied && delete a.gtmProgressiveApplied[b]
        }
    }
      , Fj = function(a, b) {
        for (var c = fa(a.F) || [], d = [], e = 0; e < c.length; e++) {
            var f = c[e];
            if (!f.gtmProgressiveApplied || !f.gtmProgressiveApplied[b]) {
                if (a.M && !Gj(f))
                    break;
                d.push(f)
            }
        }
        return d
    }
      , Gj = function(a) {
        if (ig)
            return !0;
        for (; a; ) {
            if (a.nextSibling)
                return !0;
            a = a.parentNode
        }
        return !1
    };
    var yk = function(a) {
        if (!a)
            return !1;
        if (a[Yb] && ab(a[$b])) {
            for (var b = a[$b], c = 0; c < b.length; c++)
                if (a[$b] = b[c],
                Sf(a))
                    return !0;
            return !1
        }
        return Sf(a)
    };
    var zk = 26
      , Ak = []
      , Bk = []
      , Sg = []
      , Ck = new Rf
      , Dk = []
      , Ek = []
      , qh = []
      , rh = []
      , Fk = function() {
        this.V = []
    };
    Fk.prototype.set = function(a, b) {
        this.V.push([a, b]);
        return this
    }
    ;
    Fk.prototype.resolve = function(a, b) {
        for (var c = {}, d = 0; d < this.V.length; d++) {
            var e = Vg(this.V[d][0], a, b)
              , f = Vg(this.V[d][1], a, b);
            c[e] = f
        }
        return c
    }
    ;
    var Gk = function(a) {
        this.index = a
    };
    Gk.prototype.resolve = function(a, b) {
        var c = Sg[this.index];
        if (c && !b(c)) {
            var d = c[$a];
            if (a) {
                if (a.get(d))
                    return;
                a.set(d, !0)
            }
            c = Vg(c, a, b);
            a && a.set(d, !1);
            return Sf(c)
        }
    }
    ;
    var _M = function(a) {
        return new Gk(a)
    }
      , Hk = function(a) {
        this.resolve = function(b, c) {
            for (var d = [], e = !1, f = 0; f < a.length; f++) {
                var g = Vg(Ak[a[f]], b, c);
                g === lb && (e = !0);
                d.push(g)
            }
            return e ? new Vh(d) : d.join("")
        }
    }
      , _T = function(a) {
        return new Hk(arguments)
    }
      , Ik = function(a) {
        function b(b) {
            for (var c = 1; c < a.length; c++)
                if (a[c] == b)
                    return !0;
            return !1
        }
        this.resolve = function(c, d) {
            var e = Vg(a[0], c, d);
            if (a[0]instanceof Gk && b(8) && b(16)) {
                if (e === lb)
                    return e;
                var f = Ka();
                Ck.set(f, e);
                return 'google_tag_manager["' + Ha.f + "\"].macro('" + f + "')"
            }
            e = String(e);
            for (var g = 1; g < a.length; g++)
                e = dk[a[g]](e);
            return e
        }
    }
      , _E = function(a, b) {
        return new Ik(arguments)
    }
      , Jk = function(a, b) {
        this.D = a;
        this.ya = b
    }
      , _R = function(a, b) {
        return new Jk(a,b)
    };
    var Vg = function(a, b, c) {
        var d = a;
        if (a instanceof Gk || a instanceof Fk || a instanceof Hk || a instanceof Ik)
            return a.resolve(b, c);
        if (!(a instanceof Jk))
            if (ab(a)) {
                d = [];
                for (var e = 0; e < a.length; e++)
                    d[e] = Vg(a[e], b, c)
            } else if (a && "object" == typeof a) {
                d = {};
                for (var f in a)
                    a.hasOwnProperty(f) && (d[f] = Vg(a[f], b, c))
            }
        return d
    }
      , Mk = function() {
        for (var a = [_eq, _e, '_event', _M(0), 'gtm.js', '2064523_2147479553', _ua, true, 'UA-75448111-1', false, '\x26tid', {
            10: 8
        }, 1, _u, 'Page URL', 'Page Hostname', 'host', 'Page Path', 'path', _f, 'Referrer', 'Event'], b = [], c = 0; c < a.length; c++)
            b[c] = Lk(c, a);
        return b
    }
      , Lk = function(a, b) {
        var c = b[a]
          , d = c;
        if (c instanceof Gk || c instanceof Ik || c instanceof Hk || c instanceof Jk)
            d = c;
        else if (ab(c)) {
            d = [];
            for (var e = 0; e < c.length; e++)
                d[e] = Lk(c[e], b)
        } else if ("object" == typeof c) {
            d = new Fk;
            for (var f in c)
                c.hasOwnProperty(f) && d.set(b[f], Lk(c[f], b))
        }
        return d
    }
      , Ok = function(a, b) {
        for (var c = b ? b.split(",") : [], d = 0; d < c.length; d++) {
            var e = c[d] = c[d].split(":");
            0 == a && (e[1] = Ak[e[1]]);
            if (1 == a) {
                var f = Nk(e[0]);
                e = c[d] = {};
                for (var g = 0; g < f.length; g++) {
                    var h = Bk[f[g]];
                    e[h[0]] = h[1]
                }
            }
            if (2 == a)
                for (g = 0; 4 > g; g++)
                    e[g] = Nk(e[g]);
            3 == a && (c[d] = Ak[e[0]]);
            if (4 == a)
                for (g = 0; 2 > g; g++)
                    if (e[g]) {
                        e[g] = e[g].split(".");
                        for (var k = 0; k < e[g].length; k++)
                            e[g][k] = Ak[e[g][k]]
                    } else
                        e[g] = [];
            5 == a && (c[d] = e[0])
        }
        return c
    }
      , Nk = function(a) {
        var b = [];
        if (!a)
            return b;
        for (var c = 0, d = 0; d < a.length && c < zk; c += 6,
        d++) {
            var e = a && a.charCodeAt(d) || 65;
            if (65 != e) {
                var f;
                f = 65 < e && 90 >= e ? e - 65 : 97 <= e && 122 >= e ? e - 97 + 26 : 95 == e ? 63 : 48 <= e ? e - 48 + 52 : 62;
                1 & f && b.push(c);
                2 & f && b.push(c + 1);
                4 & f && b.push(c + 2);
                8 & f && b.push(c + 3);
                16 & f && b.push(c + 4);
                32 & f && b.push(c + 5)
            }
        }
        return b
    }
      , Pk = function(a, b, c) {
        a.push.apply(a, Ok(b, c))
    };
    var Qk;
    var Ug = function(a, b) {
        if (null === a || void 0 === a)
            return a;
        if (b.propertyRenamingRequired) {
            var c = {}, d;
            for (d in a)
                if (a.hasOwnProperty(d)) {
                    var e = Tk[d];
                    e && 0 == e.indexOf("vtp_") && (c[e] = a[d])
                }
            c.__metadata = b;
            return c
        }
        return a
    }
      , Wk = function(a) {}
      , Xk = function(a, b) {}
      , Xg = function(a) {};
    var Yk, Zk;
    var jl = function(a) {
        return function() {}
    }
      , kl = function(a) {
        return function() {}
    };
    var ll = function(a) {
        var b = this;
        this.i = a;
        this.ma = this.hc = !1;
        this.Ta = [];
        this.Na = [];
        this.w = function() {
            b.ma || Wf(b.Ta);
            Zf(b, 1);
            if (Nb[a])
                for (var c = 0; c < Nb[a].length; c++)
                    Nb[a].shift().w()
        }
        ;
        this.C = function() {
            b.ma || Wf(b.Na);
            Zf(b, 2);
            if (Nb[a])
                for (var c = 0; c < Nb[a].length; c++)
                    Nb[a].shift().C()
        }
        ;
        this.H = Lf
    }
      , ml = function(a, b) {
        a.Ta.push(b)
    }
      , nl = function(a, b) {
        a.Na.push(b)
    }
      , ol = function(a) {
        this.P = [];
        this.xb = [];
        this.Rb = {};
        this.Xb = [];
        this.ca = 0;
        this.ub = {};
        this.zb = {};
        this.yb = {};
        this.event = a
    };
    ol.prototype.addListener = function(a) {
        this.Xb.push(a)
    }
    ;
    var pl = function(a) {
        0 < a.ca || Wf(a.Xb)
    }
      , ql = function(a, b, c, d, e, f) {
        if (!c.ma) {
            a.P[b] = c;
            void 0 == d && (d = []);
            void 0 == e && (e = []);
            void 0 == f && (f = []);
            d = ab(d) ? d.slice() : ["or", d];
            e = ab(e) ? e.slice() : [e];
            f = ab(f) ? f.slice() : [f];
            a.Rb[b] = d;
            a.ub[b] = 0 < e.length;
            a.zb[b] = 0 < f.length;
            a.ca++;
            var g = function() {
                0 < a.ca && !a.ub[b] && !a.zb[b] && a.ca--;
                pl(a)
            };
            ml(c, g);
            nl(c, g)
        }
    }
      , vl = function(a) {
        for (var b = [], c = {}, d = 0; d < a.P.length; c = {
            X: c.X
        },
        d++)
            if (c.X = a.P[d],
            c.X) {
                var e = a.Rb[d]
                  , f = a.ub[d]
                  , g = a.zb[d];
                if (0 != e.length || f || g) {
                    if (0 < e.length)
                        for (var h = rl(e, c.X.H), k = 0; k < e.length; k++)
                            e[k]instanceof Jk && e[k].D != d && sl(a, e[k].D, h);
                    (f || g) && tl(a, d, function(a) {
                        return function() {
                            0 < a.X.G.ca && a.X.G.ca--;
                            pl(a.X.G)
                        }
                    }(c))
                } else
                    b.push(d)
            }
        for (d = 0; d < b.length; d++)
            a.P[b[d]].H();
        for (d = 0; d < a.xb.length; d++) {
            var l = a.xb[d];
            ul(l);
            0 < l.length && l[0].H()
        }
    }
      , sl = function(a, b, c) {
        a.P[b] && (ml(a.P[b], function() {
            c(b, !0)
        }),
        nl(a.P[b], function() {
            c(b, !1)
        }))
    }
      , rl = function(a, b) {
        var c = !1;
        return function(d, e) {
            var f;
            a: {
                for (var g = 0; g < a.length; g++)
                    if (a[g]instanceof Jk && a[g].D === d || a[g] === d) {
                        f = g;
                        break a
                    }
                f = -1
            }
            c || 0 > f || ("or" == a[0] ? e ? (c = !0,
            b()) : (a.splice(f, 1),
            1 == a.length && (c = !0)) : e ? (a.splice(f, 1),
            1 == a.length && (c = !0,
            b())) : c = !0)
        }
    }
      , tl = function(a, b, c) {
        var d = []
          , e = !1
          , f = function(b) {
            var c, g, h = Ek[b];
            if (a.event.g(h)) {} else
                g = wl(h, b, a.event.g, a);
            if (c = g) {
                var k = xl(b, !0);
                0 < k.length && f(k[0].D);
                d.push(c);
                var l = xl(b, !1);
                0 < l.length && f(l[0].D)
            } else
                e = !0
        };
        f(b);
        if (!e) {
            for (var g = 0; g < d.length; g++) {
                var h = d[g]
                  , k = xl(h.i, !0);
                if (0 < k.length) {
                    var l = d[g - 1]
                      , m = yl(h);
                    ml(l, m);
                    0 == k[0].ya ? nl(l, m) : nl(l, c)
                }
                var n = xl(h.i, !1);
                0 < n.length && (m = yl(d[g + 1]),
                ml(h, m),
                0 == n[0].ya ? nl(h, m) : nl(h, c))
            }
            ml(d[d.length - 1], c);
            nl(d[d.length - 1], c);
            a.xb.push(d)
        }
    }
      , xl = function(a, b) {
        var c = b ? Oe : ef
          , d = Ek[a]
          , e = void 0 === d[c] ? [] : d[c];
        return ab(e) ? e : [e]
    }
      , yl = function(a) {
        return function() {
            a.H()
        }
    }
      , ul = function(a) {
        for (var b = [], c = 0; c < a.length; c++) {
            var d = a[c]
              , e = d.i
              , f = Mb[e]
              , g = f.firingOption;
            if (0 != g && (1 == g && void 0 !== d.G.yb[e] || 2 == g && void 0 !== f.state) && (b.push(d),
            2 == f.state && c != a.length - 1)) {
                var h = xl(a[c + 1].i, !0);
                if (0 < h.length && 1 == h[0].ya)
                    for (++c; c < a.length; c++)
                        b.push(a[c])
            }
        }
        var k = zl(b), l;
        for (l in k)
            if (k.hasOwnProperty(l)) {
                for (var m = void 0, n = void 0, p = k[l], r = p[0], t = p[p.length - 1], v, z = 0; z < a.length; z++) {
                    var J = a[z];
                    !m && J.i == r && 0 < z && (m = a[z - 1]);
                    J.i == t && z < a.length - 1 && (n = a[z + 1]);
                    if (-1 < Of(p, J.i))
                        if (v = a.splice(z, 1)[0],
                        J.i == t)
                            break;
                        else
                            z--
                }
                if (v) {
                    var F = Number(l)
                      , E = m
                      , L = n;
                    if (E) {
                        var B = E.Ta[0]
                          , D = E.Na[0]
                          , A = E;
                        A.Ta = [];
                        A.Na = [];
                        ml(E, B);
                        nl(E, D)
                    }
                    if (E && L) {
                        var C = yl(L);
                        ml(E, C);
                        var H = xl(E.i, !1);
                        0 < H.length && H[0].D != F && 0 == H[0].ya && nl(E, C);
                        var I = xl(L.i, !0);
                        0 < I.length && I[0].D != F && 0 == I[0].ya && nl(E, C)
                    }
                }
            }
    }
      , zl = function(a) {
        for (var b = {}, c = 0; c < a.length; c++) {
            var d = a[c]
              , e = []
              , f = function(a) {
                var b = xl(a, !0);
                0 < b.length && f(b[0].D);
                e.push(a);
                var c = xl(a, !1);
                0 < c.length && f(c[0].D)
            };
            f(d.i);
            b[d.i] = e
        }
        Al(a, b);
        return b
    }
      , Al = function(a, b) {
        for (var c = 0; c < a.length; c++) {
            var d = a[c].i, e;
            for (e in b)
                if (b.hasOwnProperty(e) && e != d && -1 < Of(b[e], d)) {
                    delete b[d];
                    break
                }
        }
    };
    var Bl = function(a, b, c) {
        return function() {
            a[Ad] = b.w;
            a[Bd] = b.C;
            var d = b.i
              , e = b.G && b.G.yb[d]
              , f = Mb[d] && Mb[d].state
              , g = e ? void 0 !== e : b.hc || b.ma
              , h = Mb[d] && Mb[d].firingOption
              , k = h && 2 == h
              , l = h && 1 == h;
            if (!g && void 0 === f || !g && !k || !k && !l) {
                Zf(b, 0);
                var m = b.G ? b.G.event : void 0
                  , n = a;
                n = Vg(n, new Rf, c);
                a = n;
                if (m) {}
                Sf(a, b.w, b.C)
            } else
                k && 0 == f || l && 0 == e ? Nb[d].push(b) : k && 1 == f || l && 1 == e ? b.w() : b.C()
        }
    }
      , wl = function(a, b, c, d) {
        function e(a) {
            return a.i === b
        }
        var f = function() {
            var a = d && d.P;
            return a && Pf(a, e)
        }() || new ll(b);
        f.G = d;
        ml(f, jl(a));
        nl(f, kl(a));
        f.H = Bl(a, f, c);
        return f
    };
    var Fl = !1
      , _ua = function(a, b, c) {
        function d(a) {
            var b = [].slice.call(arguments, 0);
            b[0] = n + b[0];
            y[l()].apply(window, b)
        }
        function e(b, c) {
            void 0 !== a[c] && d("set", b, a[c])
        }
        function f(a, b) {
            return void 0 === b ? b : a(b)
        }
        function g(a, b) {
            if (b)
                for (var c in b)
                    b.hasOwnProperty(c) && d("set", a + c, b[c])
        }
        function h() {
            var b = function(a, b, c) {
                if (!La(b))
                    return !1;
                for (var e = Na(Object(b), c, []), f = 0; e && f < e.length; f++)
                    d(a, e[f]);
                return !!e && 0 < e.length
            }, c;
            a[ed] ? c = Z("ecommerce") : a[dd] && (c = a[dd].ecommerce);
            if (!La(c))
                return;
            c = Object(c);
            var e = Na(a[wd], "currencyCode", c.currencyCode);
            void 0 !== e && d("set", "&cu", e);
            b("ec:addImpression", c, "impressions");
            if (b("ec:addPromo", c[c.promoClick ? "promoClick" : "promoView"], "promotions") && c.promoClick) {
                d("ec:setAction", "promo_click", c.promoClick.actionField);
                return
            }
            for (var f = "detail checkout checkout_option click add remove purchase refund".split(" "), g = 0; g < f.length; g++) {
                var h = c[f[g]];
                if (h) {
                    b("ec:addProduct", h, "products");
                    d("ec:setAction", f[g], h.actionField);
                    break
                }
            }
        }
        function k(a, b, c) {
            var d = 0;
            if (void 0 !== a)
                for (var e in a)
                    if (a.hasOwnProperty(e) && (c && t[e] || !c && void 0 === t[e])) {
                        var f = v[e] ? Oa(a[e]) : a[e];
                        "anonymizeIp" != e || f || (f = void 0);
                        b[e] = f;
                        d++
                    }
            return d
        }
        hb("GoogleAnalyticsObject", a[ee] || "ga");
        var l = function() {
            return y.GoogleAnalyticsObject
        }
          , m = hb(l(), function() {
            var a = y[l()];
            a.q = a.q || [];
            a.q.push(arguments)
        });
        m.l = Number(Y());
        var n = ""
          , p = "";
        "string" != typeof a[sf] ? (p = Ka(),
        n = p + ".") : "" !== a[sf] && (p = a[sf],
        n = p + ".");
        var r = !1;
        var z = {
            name: p
        };
        m("create", a[Pb], z);
        d("set", "&gtm", ya(!0));
        var F;
        a[Ud] && d("require", "linkid", "linkid.js");
        d("set", "hitCallback", function() {
            if (R(a[Cd]))
                a[Cd]();
            else {
                var c = a[wd]
                  , d = c && c.hitCallback;
                R(d) && d()
            }
            b()
        });
        if (a[of]) {} else if (a[pf]) {} else if (a[rf]) {} else if (a[qf]) {} else if (a[Vc]) {} else if (a[Tc]) {} else if (a[nf]) {} else {
            a[ld] && (d("require", "ec", "ec.js"),
            h());
            if (a[cd] && !a[nd]) {
                var I = "_dc_gtm_" + String(a[Pb]).replace(/[^A-Za-z0-9-]/g, "");
                d("require", "displayfeatures", void 0, {
                    cookieName: I
                })
            }
            F ? d("send", "pageview", F) : d("send", "pageview");
        }
        if (!Fl) {
            var N = a[Rc] ? "u/analytics_debug.js" : "analytics.js";
            a[Kd] && !a[Rc] && (N = "internal/" + N);
            Fl = !0;
            u(ib("https:", "http:", "//www.google-analytics.com/" + N, r), function() {
                y[l()].loaded || c()
            }, c)
        }
    };
    _ua.a = "ua";
    _ua.b = ["google"];
    var Il = function() {
        var a = [];
        return function(b, c) {
            if (void 0 === a[b]) {
                var d = Dk[b] && Vg(Dk[b], new Rf, c)
                  , e = d;
                d && (e = yk(d));
                a[b] = [e, d]
            }
            return a[b]
        }
    }
      , Jl = function(a, b) {
        for (var c = b[0], d = 0; d < c.length; d++)
            if (!a.ba(c[d], a.g)[0])
                return !1;
        var e = b[2];
        for (d = 0; d < e.length; d++)
            if (a.ba(e[d], a.g)[0])
                return !1;
        return !0
    }
      , Kl = !1;
    Lg = function(a, b, c, d, e) {
        switch (b) {
        case "gtm.js":
            if (Kl)
                return !1;
            Kl = !0;
            break;
        case "gtm.sync":
            if (Z("gtm.snippet") != Jb)
                return !1
        }
        for (var f = {
            id: a,
            name: b,
            Ga: d || Lf,
            ka: Nk(),
            Ra: Nk(),
            ba: Il(),
            g: Rg(c)
        }, g = [], h = 0; h < qh.length; h++)
            if (Jl(f, qh[h])) {
                g[h] = !0;
                for (var k = f, l = qh[h], m = l[1], n = 0; n < m.length; n++)
                    k.ka[m[n]] = !0;
                var p = l[3];
                for (n = 0; n < p.length; n++)
                    k.Ra[p[n]] = !0
            } else
                g[h] = !1;
        var Q = [];
        for (var M = 0; M < zk; M++)
            if (f.ka[M] && !f.Ra[M])
                if (f.g(Ek[M])) {} else {
                    Q[M] = Ek[M];
                }
        f.va = Q;
        for (var ma = new ol(f), da = 0; da < zk; da++)
            if (f.ka[da] && !f.Ra[da])
                if (f.g(Ek[da])) {} else {
                    var Ma = f.va[da]
                      , Lj = wl(Ma, da, f.g, ma);
                    ql(ma, da, Lj, Ma[Yc], Ma[Oe], Ma[ef]);
                    if (Ma[Ob])
                        break
                }
        ma.addListener(f.Ga);
        vl(ma);
        pl(ma);
        e && R(e) && e({
            passingRules: g,
            resolvedTags: f.va
        });
        if ("gtm.js" == b || "gtm.sync" == b)
            a: {}
        for (var bg in f.va)
            if (f.va.hasOwnProperty(bg)) {
                var cg = f.va[bg];
                if (void 0 == cg[$a] || !$f(cg[$a], "_implicit"))
                    return !0
            }
        return !1
    }
    ;
    var Ml = function() {};
    var Nl = {};
    var Sl = function() {};
    var Ll = {
        macro: function(a) {
            if (Ck.contains(a))
                return Ck.get(a)
        }
    };
    Ll.dataLayer = zg;
    Ll.onHtmlSuccess = Yh(!0);
    Ll.onHtmlFailure = Yh(!1);
    Ll.callback = function(a) {
        kb.hasOwnProperty(a) && R(kb[a]) && kb[a]();
        delete kb[a]
    }
    ;
    Ll.Dc = function() {
        var a = y.google_tag_manager;
        a || (a = y.google_tag_manager = {});
        sb = a;
        if (a[Ha.f]) {
            var b = sb.zones;
            b && b.unregisterChild(Ha.f)
        } else {
            a[Ha.f] = Ll;
            ji();
            uh();
            Ak.push.apply(Ak, Mk());
            Pk(Bk, 0, "10:0,10:1,11:2,2:3,3:4,10:6,13:7,0:8,9:9,8:9,15:9,5:9,6:9,1:11,12:9,7:9,14:12,10:13,11:14,11:15,4:16,11:17,4:18,10:19,11:20,11:21");
            Pk(Sg, 1, "G,AAgB,AAgG,AAgY,AAAgB,CAAAC");
            Pk(Dk, 1, "Z");
            Pk(Ek, 1, "g_f");
            Pk(qh, 2, "B:B::");
            Pk(rh, 4, "5:");
            for (var c = 0; c < Ek.length; c++) {
                var d = Ek[c]
                  , e = 1;
                d[le] ? e = 2 : d[xf] && (e = 0);
                Mb[c] = {
                    firingOption: e,
                    state: void 0
                };
                Nb[c] = []
            }
            Ig();
            $g();
            var n = y;
            if ("interactive" == K.readyState && !K.createEventObject || "complete" == K.readyState)
                kg();
            else {
                va(K, "DOMContentLoaded", kg);
                va(K, "readystatechange", kg);
                if (K.createEventObject && K.documentElement.doScroll) {
                    var p = !0;
                    try {
                        p = !n.frameElement
                    } catch (J) {}
                    p && mg()
                }
                va(n, "load", kg)
            }
            "complete" === K.readyState ? rg() : va(y, "load", rg);
            Sl();
            Ml();
            a: {}
        }
    }
    ;
    Ll.Dc();
    var _vs = "res_ts:1458643679293000,srv_cl:187630136,ds:live,cv:1";
}
)()