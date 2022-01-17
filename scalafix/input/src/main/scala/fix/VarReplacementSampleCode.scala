/*
rule = AddContextVarV1
*/
package fix

import scala.Int
import scala.Boolean

trait VarReplacementSampleCode {
  def fun21b() = {val b = (); s"s"}
  def fun21c(): Unit = {()}
  def fun10()

  def fun0a
  def fun0()
  def fun0(i: Int)
  def fun0()(implicit c: Int, b: Int)
  def fun0(implicit c: Int, b: Int)

  def fun1a: Unit
  def fun1(): Unit
  def fun1(i: Int): Unit
  def fun1b(i: Int)(): Unit
  def fun1()(implicit c: Int, b: Int): Unit
  def fun1(implicit c: Int, b: Int): Unit

  def fun2 = {val b = (); s"s"}
  def fun2b() = {val b = (); s"s"}
  def fun2c(): Unit = {()}
  def fun2(i: Int): Unit = {()}
  def fun2b(i: Int)(): Unit = {()}
  def fun2(i: Int)(a: Int)(f: Int => Int)(implicit b: Int): Unit = {()}
  def fun211(i: Int, j: Int)(a: Int)(f: Int => Int)(implicit bi: Int): Unit = {()}
  def fun211(i: Int)(a: Int)(f: Int => Int)(implicit bi: Int) = {()}
}
