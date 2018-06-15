import execjs

def ras(n, k):
    ctx = execjs.compile("""
    function RSAKeyPair(b, c, a) {
        this.e = biFromHex(b);
        this.d = biFromHex(c);
        this.m = biFromHex(a);
        this.chunkSize = 2 * biHighIndex(this.m);
        this.radix = 16;
        this.barrett = new BarrettMu(this.m)
    }

    function twoDigit(a) {
        return (a < 10 ? "0" : "") + String(a)
    }

    function encryptedString(l, o) {
        var h = new Array();
        var b = o.length;
        var f = 0;
        while (f < b) {
            h[f] = o.charCodeAt(f);
            f++
        }
        while (h.length % l.chunkSize != 0) {
            h[f++] = 0
        }
        var g = h.length;
        var p = "";
        var e, d, c;
        for (f = 0; f < g; f += l.chunkSize) {
            c = new BigInt();
            e = 0;
            for (d = f; d < f + l.chunkSize; ++e) {
                c.digits[e] = h[d++];
                c.digits[e] += h[d++] << 8
            }
            var n = l.barrett.powMod(c, l.e);
            var m = l.radix == 16 ? biToHex(n) : biToString(n, l.radix);
            p += m + " "
        }
        return p.substring(0, p.length - 1)
    }

    function decryptedString(e, f) {
        var h = f.split(" ");
        var a = "";
        var d, c, g;
        for (d = 0; d < h.length; ++d) {
            var b;
            if (e.radix == 16) {
                b = biFromHex(h[d])
            } else {
                b = biFromString(h[d], e.radix)
            }
            g = e.barrett.powMod(b, e.d);
            for (c = 0; c <= biHighIndex(g); ++c) {
                a += String.fromCharCode(g.digits[c] & 255, g.digits[c] >> 8)
            }
        }
        if (a.charCodeAt(a.length - 1) == 0) {
            a = a.substring(0, a.length - 1)
        }
        return a
    }
    var biRadixBase = 2;
    var biRadixBits = 16;
    var bitsPerDigit = biRadixBits;
    var biRadix = 1 << 16;
    var biHalfRadix = biRadix >>> 1;
    var biRadixSquared = biRadix * biRadix;
    var maxDigitVal = biRadix - 1;
    var maxInteger = 9999999999999998;
    var maxDigits;
    var ZERO_ARRAY;
    var bigZero, bigOne;

    function setMaxDigits(b) {
        maxDigits = b;
        ZERO_ARRAY = new Array(maxDigits);
        for (var a = 0; a < ZERO_ARRAY.length; a++) {
            ZERO_ARRAY[a] = 0
        }
        bigZero = new BigInt();
        bigOne = new BigInt();
        bigOne.digits[0] = 1
    }
    setMaxDigits(20);
    var dpl10 = 15;
    var lr10 = biFromNumber(1000000000000000);

    function BigInt(a) {
        if (typeof a == "boolean" && a == true) {
            this.digits = null
        } else {
            this.digits = ZERO_ARRAY.slice(0)
        }
        this.isNeg = false
    }

    function biFromDecimal(e) {
        var d = e.charAt(0) == "-";
        var c = d ? 1 : 0;
        var a;
        while (c < e.length && e.charAt(c) == "0") {
            ++c
        }
        if (c == e.length) {
            a = new BigInt()
        } else {
            var b = e.length - c;
            var f = b % dpl10;
            if (f == 0) {
                f = dpl10
            }
            a = biFromNumber(Number(e.substr(c, f)));
            c += f;
            while (c < e.length) {
                a = biAdd(biMultiply(a, lr10), biFromNumber(Number(e.substr(c, dpl10))));
                c += dpl10
            }
            a.isNeg = d
        }
        return a
    }

    function biCopy(b) {
        var a = new BigInt(true);
        a.digits = b.digits.slice(0);
        a.isNeg = b.isNeg;
        return a
    }

    function biFromNumber(c) {
        var a = new BigInt();
        a.isNeg = c < 0;
        c = Math.abs(c);
        var b = 0;
        while (c > 0) {
            a.digits[b++] = c & maxDigitVal;
            c >>= biRadixBits
        }
        return a
    }

    function reverseStr(c) {
        var a = "";
        for (var b = c.length - 1; b > -1; --b) {
            a += c.charAt(b)
        }
        return a
    }
    var hexatrigesimalToChar = new Array("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z");

    function biToString(d, f) {
        var c = new BigInt();
        c.digits[0] = f;
        var e = biDivideModulo(d, c);
        var a = hexatrigesimalToChar[e[1].digits[0]];
        while (biCompare(e[0], bigZero) == 1) {
            e = biDivideModulo(e[0], c);
            digit = e[1].digits[0];
            a += hexatrigesimalToChar[e[1].digits[0]]
        }
        return (d.isNeg ? "-" : "") + reverseStr(a)
    }

    function biToDecimal(d) {
        var c = new BigInt();
        c.digits[0] = 10;
        var e = biDivideModulo(d, c);
        var a = String(e[1].digits[0]);
        while (biCompare(e[0], bigZero) == 1) {
            e = biDivideModulo(e[0], c);
            a += String(e[1].digits[0])
        }
        return (d.isNeg ? "-" : "") + reverseStr(a)
    }
    var hexToChar = new Array("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f");

    function digitToHex(c) {
        var b = 15;
        var a = "";
        for (i = 0; i < 4; ++i) {
            a += hexToChar[c & b];
            c >>>= 4
        }
        return reverseStr(a)
    }

    function biToHex(b) {
        var a = "";
        var d = biHighIndex(b);
        for (var c = biHighIndex(b); c > -1; --c) {
            a += digitToHex(b.digits[c])
        }
        return a
    }

    function charToHex(k) {
        var d = 48;
        var b = d + 9;
        var e = 97;
        var h = e + 25;
        var g = 65;
        var f = 65 + 25;
        var a;
        if (k >= d && k <= b) {
            a = k - d
        } else {
            if (k >= g && k <= f) {
                a = 10 + k - g
            } else {
                if (k >= e && k <= h) {
                    a = 10 + k - e
                } else {
                    a = 0
                }
            }
        }
        return a
    }

    function hexToDigit(d) {
        var b = 0;
        var a = Math.min(d.length, 4);
        for (var c = 0; c < a; ++c) {
            b <<= 4;
            b |= charToHex(d.charCodeAt(c))
        }
        return b
    }

    function biFromHex(e) {
        var b = new BigInt();
        var a = e.length;
        for (var d = a, c = 0; d > 0; d -= 4, ++c) {
            b.digits[c] = hexToDigit(e.substr(Math.max(d - 4, 0), Math.min(d, 4)))
        }
        return b
    }

    function biFromString(l, k) {
        var a = l.charAt(0) == "-";
        var e = a ? 1 : 0;
        var m = new BigInt();
        var b = new BigInt();
        b.digits[0] = 1;
        for (var d = l.length - 1; d >= e; d--) {
            var f = l.charCodeAt(d);
            var g = charToHex(f);
            var h = biMultiplyDigit(b, g);
            m = biAdd(m, h);
            b = biMultiplyDigit(b, k)
        }
        m.isNeg = a;
        return m
    }

    function biDump(a) {
        return (a.isNeg ? "-" : "") + a.digits.join(" ")
    }

    function biAdd(b, g) {
        var a;
        if (b.isNeg != g.isNeg) {
            g.isNeg = !g.isNeg;
            a = biSubtract(b, g);
            g.isNeg = !g.isNeg
        } else {
            a = new BigInt();
            var f = 0;
            var e;
            for (var d = 0; d < b.digits.length; ++d) {
                e = b.digits[d] + g.digits[d] + f;
                a.digits[d] = e & 65535;
                f = Number(e >= biRadix)
            }
            a.isNeg = b.isNeg
        }
        return a
    }

    function biSubtract(b, g) {
        var a;
        if (b.isNeg != g.isNeg) {
            g.isNeg = !g.isNeg;
            a = biAdd(b, g);
            g.isNeg = !g.isNeg
        } else {
            a = new BigInt();
            var f, e;
            e = 0;
            for (var d = 0; d < b.digits.length; ++d) {
                f = b.digits[d] - g.digits[d] + e;
                a.digits[d] = f & 65535;
                if (a.digits[d] < 0) {
                    a.digits[d] += biRadix
                }
                e = 0 - Number(f < 0)
            }
            if (e == -1) {
                e = 0;
                for (var d = 0; d < b.digits.length; ++d) {
                    f = 0 - a.digits[d] + e;
                    a.digits[d] = f & 65535;
                    if (a.digits[d] < 0) {
                        a.digits[d] += biRadix
                    }
                    e = 0 - Number(f < 0)
                }
                a.isNeg = !b.isNeg
            } else {
                a.isNeg = b.isNeg
            }
        }
        return a
    }

    function biHighIndex(b) {
        var a = b.digits.length - 1;
        while (a > 0 && b.digits[a] == 0) {
            --a
        }
        return a
    }

    function biNumBits(c) {
        var f = biHighIndex(c);
        var e = c.digits[f];
        var b = (f + 1) * bitsPerDigit;
        var a;
        for (a = b; a > b - bitsPerDigit; --a) {
            if ((e & 32768) != 0) {
                break
            }
            e <<= 1
        }
        return a
    }

    function biMultiply(h, g) {
        var o = new BigInt();
        var f;
        var b = biHighIndex(h);
        var m = biHighIndex(g);
        var l, a, d;
        for (var e = 0; e <= m; ++e) {
            f = 0;
            d = e;
            for (j = 0; j <= b; ++j, ++d) {
                a = o.digits[d] + h.digits[j] * g.digits[e] + f;
                o.digits[d] = a & maxDigitVal;
                f = a >>> biRadixBits
            }
            o.digits[e + b + 1] = f
        }
        o.isNeg = h.isNeg != g.isNeg;
        return o
    }

    function biMultiplyDigit(a, g) {
        var f, e, d;
        result = new BigInt();
        f = biHighIndex(a);
        e = 0;
        for (var b = 0; b <= f; ++b) {
            d = result.digits[b] + a.digits[b] * g + e;
            result.digits[b] = d & maxDigitVal;
            e = d >>> biRadixBits
        }
        result.digits[1 + f] = e;
        return result
    }

    function arrayCopy(e, h, c, g, f) {
        var a = Math.min(h + f, e.length);
        for (var d = h, b = g; d < a; ++d, ++b) {
            c[b] = e[d]
        }
    }
    var highBitMasks = new Array(0, 32768, 49152, 57344, 61440, 63488, 64512, 65024, 65280, 65408, 65472, 65504, 65520, 65528, 65532, 65534, 65535);

    function biShiftLeft(b, h) {
        var d = Math.floor(h / bitsPerDigit);
        var a = new BigInt();
        arrayCopy(b.digits, 0, a.digits, d, a.digits.length - d);
        var g = h % bitsPerDigit;
        var c = bitsPerDigit - g;
        for (var e = a.digits.length - 1, f = e - 1; e > 0; --e, --f) {
            a.digits[e] = ((a.digits[e] << g) & maxDigitVal) | ((a.digits[f] & highBitMasks[g]) >>> (c))
        }
        a.digits[0] = ((a.digits[e] << g) & maxDigitVal);
        a.isNeg = b.isNeg;
        return a
    }
    var lowBitMasks = new Array(0, 1, 3, 7, 15, 31, 63, 127, 255, 511, 1023, 2047, 4095, 8191, 16383, 32767, 65535);

    function biShiftRight(b, h) {
        var c = Math.floor(h / bitsPerDigit);
        var a = new BigInt();
        arrayCopy(b.digits, c, a.digits, 0, b.digits.length - c);
        var f = h % bitsPerDigit;
        var g = bitsPerDigit - f;
        for (var d = 0, e = d + 1; d < a.digits.length - 1; ++d, ++e) {
            a.digits[d] = (a.digits[d] >>> f) | ((a.digits[e] & lowBitMasks[f]) << g)
        }
        a.digits[a.digits.length - 1] >>>= f;
        a.isNeg = b.isNeg;
        return a
    }

    function biMultiplyByRadixPower(b, c) {
        var a = new BigInt();
        arrayCopy(b.digits, 0, a.digits, c, a.digits.length - c);
        return a
    }

    function biDivideByRadixPower(b, c) {
        var a = new BigInt();
        arrayCopy(b.digits, c, a.digits, 0, a.digits.length - c);
        return a
    }

    function biModuloByRadixPower(b, c) {
        var a = new BigInt();
        arrayCopy(b.digits, 0, a.digits, 0, c);
        return a
    }

    function biCompare(a, c) {
        if (a.isNeg != c.isNeg) {
            return 1 - 2 * Number(a.isNeg)
        }
        for (var b = a.digits.length - 1; b >= 0; --b) {
            if (a.digits[b] != c.digits[b]) {
                if (a.isNeg) {
                    return 1 - 2 * Number(a.digits[b] > c.digits[b])
                } else {
                    return 1 - 2 * Number(a.digits[b] < c.digits[b])
                }
            }
        }
        return 0
    }

    function biDivideModulo(g, f) {
        var a = biNumBits(g);
        var e = biNumBits(f);
        var d = f.isNeg;
        var o, m;
        if (a < e) {
            if (g.isNeg) {
                o = biCopy(bigOne);
                o.isNeg = !f.isNeg;
                g.isNeg = false;
                f.isNeg = false;
                m = biSubtract(f, g);
                g.isNeg = true;
                f.isNeg = d
            } else {
                o = new BigInt();
                m = biCopy(g)
            }
            return new Array(o, m)
        }
        o = new BigInt();
        m = g;
        var k = Math.ceil(e / bitsPerDigit) - 1;
        var h = 0;
        while (f.digits[k] < biHalfRadix) {
            f = biShiftLeft(f, 1);
            ++h;
            ++e;
            k = Math.ceil(e / bitsPerDigit) - 1
        }
        m = biShiftLeft(m, h);
        a += h;
        var u = Math.ceil(a / bitsPerDigit) - 1;
        var B = biMultiplyByRadixPower(f, u - k);
        while (biCompare(m, B) != -1) {
            ++o.digits[u - k];
            m = biSubtract(m, B)
        }
        for (var z = u; z > k; --z) {
            var l = (z >= m.digits.length) ? 0 : m.digits[z];
            var A = (z - 1 >= m.digits.length) ? 0 : m.digits[z - 1];
            var w = (z - 2 >= m.digits.length) ? 0 : m.digits[z - 2];
            var v = (k >= f.digits.length) ? 0 : f.digits[k];
            var c = (k - 1 >= f.digits.length) ? 0 : f.digits[k - 1];
            if (l == v) {
                o.digits[z - k - 1] = maxDigitVal
            } else {
                o.digits[z - k - 1] = Math.floor((l * biRadix + A) / v)
            }
            var s = o.digits[z - k - 1] * ((v * biRadix) + c);
            var p = (l * biRadixSquared) + ((A * biRadix) + w);
            while (s > p) {
                --o.digits[z - k - 1];
                s = o.digits[z - k - 1] * ((v * biRadix) | c);
                p = (l * biRadix * biRadix) + ((A * biRadix) + w)
            }
            B = biMultiplyByRadixPower(f, z - k - 1);
            m = biSubtract(m, biMultiplyDigit(B, o.digits[z - k - 1]));
            if (m.isNeg) {
                m = biAdd(m, B);
                --o.digits[z - k - 1]
            }
        }
        m = biShiftRight(m, h);
        o.isNeg = g.isNeg != d;
        if (g.isNeg) {
            if (d) {
                o = biAdd(o, bigOne)
            } else {
                o = biSubtract(o, bigOne)
            }
            f = biShiftRight(f, h);
            m = biSubtract(f, m)
        }
        if (m.digits[0] == 0 && biHighIndex(m) == 0) {
            m.isNeg = false
        }
        return new Array(o, m)
    }

    function biDivide(a, b) {
        return biDivideModulo(a, b)[0]
    }

    function biModulo(a, b) {
        return biDivideModulo(a, b)[1]
    }

    function biMultiplyMod(b, c, a) {
        return biModulo(biMultiply(b, c), a)
    }

    function biPow(c, e) {
        var b = bigOne;
        var d = c;
        while (true) {
            if ((e & 1) != 0) {
                b = biMultiply(b, d)
            }
            e >>= 1;
            if (e == 0) {
                break
            }
            d = biMultiply(d, d)
        }
        return b
    }

    function biPowMod(d, g, c) {
        var b = bigOne;
        var e = d;
        var f = g;
        while (true) {
            if ((f.digits[0] & 1) != 0) {
                b = biMultiplyMod(b, e, c)
            }
            f = biShiftRight(f, 1);
            if (f.digits[0] == 0 && biHighIndex(f) == 0) {
                break
            }
            e = biMultiplyMod(e, e, c)
        }
        return b
    }

    function BarrettMu(a) {
        this.modulus = biCopy(a);
        this.k = biHighIndex(this.modulus) + 1;
        var b = new BigInt();
        b.digits[2 * this.k] = 1;
        this.mu = biDivide(b, this.modulus);
        this.bkplus1 = new BigInt();
        this.bkplus1.digits[this.k + 1] = 1;
        this.modulo = BarrettMu_modulo;
        this.multiplyMod = BarrettMu_multiplyMod;
        this.powMod = BarrettMu_powMod
    }

    function BarrettMu_modulo(h) {
        var g = biDivideByRadixPower(h, this.k - 1);
        var e = biMultiply(g, this.mu);
        var d = biDivideByRadixPower(e, this.k + 1);
        var c = biModuloByRadixPower(h, this.k + 1);
        var k = biMultiply(d, this.modulus);
        var b = biModuloByRadixPower(k, this.k + 1);
        var a = biSubtract(c, b);
        if (a.isNeg) {
            a = biAdd(a, this.bkplus1)
        }
        var f = biCompare(a, this.modulus) >= 0;
        while (f) {
            a = biSubtract(a, this.modulus);
            f = biCompare(a, this.modulus) >= 0
        }
        return a
    }

    function BarrettMu_multiplyMod(a, c) {
        var b = biMultiply(a, c);
        return this.modulo(b)
    }

    function BarrettMu_powMod(c, f) {
        var b = new BigInt();
        b.digits[0] = 1;
        var d = c;
        var e = f;
        while (true) {
            if ((e.digits[0] & 1) != 0) {
                b = this.multiplyMod(b, d)
            }
            e = biShiftRight(e, 1);
            if (e.digits[0] == 0 && biHighIndex(e) == 0) {
                break
            }
            d = this.multiplyMod(d, d)
        }
        return b
    }

    function encryptForm(a, g, c) {
        var h = c.maxdigits;
        var f = c.e;
        var k = c.n;
        setMaxDigits(h);
        var b = new RSAKeyPair(f, "", k);
        $.each(a, function(d, m) {
            var e = m.name;
            var l = m.value;
            if (l !== null && l !== "" && $.inArray(e, g) > -1) {
                m.value = encryptedString(b, l)
            }
        });
        return a
    };

    function encryptPwd(v, k){
        var h = 67;
        var f = "10001";
        setMaxDigits(h);
        var b = new RSAKeyPair(f, "", k);
        return encryptedString(b, v);

    }

    """)
    #var k = '8c72bc73c06bd00927a01942f7bb3c8300dde2886bbf0ca1bedfffb04901155c89cc7d6859992c030f4145681f97ff328cf5136c5c0ad174f35a0136af5054a9';
    return ctx.call('encryptPwd',n, k)
if __name__ == '__main__':
    print ras('18331414')

