
## 数值安全的 Softmax

原始的 softmax 的公式是：

$$
 softmax(x_i) = \frac{ e ^ {x_i} }{ \sum_{j=1}^{N} e ^ {x_j} }
$$
非常大的 $e ^ {x_i}$ 会比较容易产生 overflow，比如 float16 最大值是 65536，如果 $x \ge 11$，就会溢出。为了应对这个问题，一般工程上都会做一个 ”数值安全“ 处理，使每个 $x_i$ 减去 $x$ 中的最大值 $m$：
	
$$ 
softmax(x_i) =
  \frac{ e ^ { x_i } }{ \sum_{j=1}^{N} e ^ { x_j }  } = 
  \frac{ e ^ { x_i  - m } }{ \sum_{j=1}^{N} e ^ { x_j - m }  }
$$

不要这个 $m$ 是一个全局状态，需要在遍历完 $x$ 之后才可以得到它，而计算出最后的 softmax 值，必须依赖这个前置的 $m$ 才能做后续的计算。能不能把 $x$ 拆分成小块，让 softmax 操作可以分开跑？

## Softmax tiling

假设有一个向量 $x=[x^{(1)} \space  x^{(2)}] \in R^{2B}$，它的长度为 $2B$，将这个向量分成两个长度为 $B$ 的子向量，针对其中的一个子向量 $x^{(1)}$：

$$
\begin{aligned}
  m(x^{(1)}) &= max_i(x^{(1)}_i) \\
  f(x^{(1)}) &= [ e^{x^{(1)}_1-m(x)} ... e^{x^{(1)}_B-m(x)} ] \\
  l(x^{(1)}) &= \sum_i{ f(x^{(1)})_i } \\
  softmax(x^{(1)}) &= \frac{f(x^{(1)})}{l(x^{(1)})}
\end{aligned}
$$

已知两个子向量的最大值，求新的最大值很直接：

$$
  m(x) = m([x^{(1)} x^{(2)}]) = max(m(x^{(1)}), m(x^{(2)}))
$$

$f(x)$ 的处理上有一点差异，$f(x^{(1)})$ 中指数项减去的是 $x^{(1)}$ 中的局部最大值 $m(x^{(1)})$，而 $f(x)$ 中需要减去的全局最大值是 $m(x)$。

$$
\begin{aligned}
  f(x) & = [e^{x_i-m(x)}...e^{x_{2B}-m(x)}] \\
       & = [e^{x_i-m(x^{(1)})+m(x^{(1)})-m(x)}...e^{x_{2B}-m(x^{(2)})+m(x^{(2)})-m(x)}] \\
       & = [ 
         e^{m(x^{(1)})-m(x)} f(x^{(1)}) \,\,\,\,
         e^{m(x^{(2)})-m(x)} f(x^{(2)}) ] \\
\end{aligned}
$$
可见基于两个子向量的 $f(x^{(1)})$ 和 $f(x^{(2)})$，和 $m(x^{(1)})$ 和 $m(x^{(2)})$，可以求出完整向量的 $f(x)$。

$l(x)$ 的计算类似：

$$
l(x) = e^{m(x^{(1)})-m(x)} l(x^{(1)}) +
         e^{m(x^{(2)})-m(x)} l(x^{(2)})
$$

不过这里还不大理想，按说 $f(x^{(1)})$ 和 $f(x^{(2)})$ 都是向量，在找到全局最大 $m(x)$ 回来算 $f(x)$ 仍然得遍历一遍 $f(x^{(1)})$ 和 $f(x^{(2)})$，仍然至少需要两轮迭代才能求出 softmax 结果的向量。


## References
- https://zhuanlan.zhihu.com/p/621272925
- Online normalizer calculation for softmax
- [[From Online Softmax to FlashAttention]]


